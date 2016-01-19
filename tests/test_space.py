from __future__ import with_statement
import sys
import unittest
import warnings

import pymunk as p
from pymunk import *
from pymunk.vec2d import Vec2d

####################################################################

class UnitTestSpace(unittest.TestCase):
    def setUp(self):
        p.reset_shapeid_counter()

        self.s = p.Space()

        self.b1, self.b2 = p.Body(1,3),p.Body(10,100)
        self.s.add(self.b1,self.b2)
        self.b1.position = 10,0
        self.b2.position = 20,0

        self.s1,self.s2 = p.Circle(self.b1,5), p.Circle(self.b2,10)
        self.s.add(self.s1,self.s2)

    def tearDown(self):
        del self.s
        del self.b1, self.b2
        del self.s1, self.s2

    def testProperties(self):
        s = p.Space()

        self.assertEqual(s.iterations, 10)
        s.iterations = 15
        self.assertEqual(s.iterations, 15)

        self.assertEqual(s.gravity, (0,0))
        s.gravity = 10,2
        self.assertEqual(s.gravity, (10,2))
        self.assertEqual(s.gravity.x, 10)

        self.assertEqual(s.damping, 1)
        s.damping = 3
        self.assertEqual(s.damping, 3)

        self.assertEqual(s.idle_speed_threshold, 0)
        s.idle_speed_threshold = 4
        self.assertEqual(s.idle_speed_threshold, 4)

        self.assertEqual(str(s.sleep_time_threshold), 'inf')
        s.sleep_time_threshold = 5
        self.assertEqual(s.sleep_time_threshold, 5)

        self.assertAlmostEqual(s.collision_slop, 0.1)
        s.collision_slop = 6
        self.assertEqual(s.collision_slop, 6)

        self.assertAlmostEqual(s.collision_bias, 0.0017970074436)
        s.collision_bias = 0.2
        self.assertEqual(s.collision_bias, 0.2)

        self.assertEqual(s.collision_persistence, 3)
        s.collision_persistence = 9
        self.assertEqual(s.collision_persistence, 9)

        self.assertEqual(s.current_time_step, 0)
        s.step(0.1)
        self.assertEqual(s.current_time_step, 0.1)

        self.assertTrue(s.static_body != None)
        self.assertEqual(s.static_body.body_type, p.Body.STATIC)

    def testAddRemove(self):
        s = p.Space()

        self.assertEqual(s.bodies, [])
        self.assertEqual(s.shapes, [])

        b = p.Body(1,2)
        s.add(b)
        self.assertEqual(s.bodies, [b])
        self.assertEqual(s.shapes, [])

        c1 = p.Circle(b, 10)
        s.add(c1)
        self.assertEqual(s.bodies, [b])
        self.assertEqual(s.shapes, [c1])

        c2 = p.Circle(b, 15)
        s.add(c2)
        self.assertEqual(s.shapes, [c1,c2])

        s.remove(c1)
        self.assertEqual(s.shapes, [c2])

        s.remove(c2, b)
        self.assertEqual(s.bodies, [])
        self.assertEqual(s.shapes, [])

        s.add(c2, b)
        self.assertEqual(s.bodies, [b])
        self.assertEqual(s.shapes, [c2])

    def testAddRemoveInStep(self):
        s = p.Space()

        b1 = p.Body(1, 2)
        c1 = p.Circle(b1, 2)

        b2 = p.Body(1, 2)
        c2 = p.Circle(b2, 2)

        s.add(b1, b2, c1, c2)

        b = p.Body(1, 2)
        c = p.Circle(b, 2)
        def pre_solve1(space, arbiter):
            space.add(b, c)
            self.assertTrue(b not in s.bodies)
            self.assertTrue(c not in s.shapes)

        def pre_solve2(space, arbiter):
            space.remove(b, c)
            self.assertTrue(b not in s.bodies)
            self.assertTrue(c not in s.shapes)

            space.add(b, c)
            return True

        s.collision_handler(0, 0).pre_solve = pre_solve1

        s.step(.1)
        self.assertTrue(b in s.bodies)
        self.assertTrue(c in s.shapes)

        self.assert_(b in s.bodies)
        self.assert_(c in s.shapes)

    def testRemoveInStep(self):
        s = self.s

        def pre_solve(space, arbiter):
            space.remove(arbiter.shapes)
            return True

        s.collision_handler(0, 0).pre_solve = pre_solve

        s.step(.1)

        self.assert_(self.s1 not in s.bodies)
        self.assert_(self.s2 not in s.shapes)

    def testPointQuery(self):
        s = p.Space()
        b1 = p.Body(1, 1)
        b1.position = 19, 0
        s1 = p.Circle(b1, 10)
        s.add(s1)

        b2 = p.Body(1, 1)
        b2.position = 0, 0
        s2 = p.Circle(b2, 10)
        s.add(s2)

        hits = s.point_query((23,0), 0, p.ShapeFilter())

        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].shape, s1)
        self.assertEqual(hits[0].point, (29,0))
        self.assertEqual(hits[0].distance, -6)
        self.assertEqual(hits[0].gradient, (1,0))

        hits = s.point_query((30,0), 0, p.ShapeFilter())
        self.assertEqual(len(hits), 0)

        hits = s.point_query((30,0), 30, p.ShapeFilter())
        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0].shape, s2)
        self.assertEqual(hits[0].point, (10,0))
        self.assertEqual(hits[0].distance, 20)
        self.assertEqual(hits[0].gradient, (1,0))

        self.assertEqual(hits[1].shape, s1)
        self.assertEqual(hits[1].point, (29,0))
        self.assertEqual(hits[1].distance, 1)
        self.assertEqual(hits[1].gradient, (1,0))

    def testPointQueryNearest(self):
        s = p.Space()
        b1 = p.Body(1,1)
        b1.position = 19,0
        s1 = p.Circle(b1, 10)
        s.add(s1)

        hit = s.point_query_nearest((23,0), 0, p.ShapeFilter())
        self.assertEqual(hit.shape, s1)
        self.assertEqual(hit.point, (29,0))
        self.assertEqual(hit.distance, -6)
        self.assertEqual(hit.gradient, (1,0))

        hit = s.point_query_nearest((30,0), 0, p.ShapeFilter())
        self.assertEqual(hit, None)

        hit = s.point_query_nearest((30,0), 10, p.ShapeFilter())
        self.assertEqual(hit.shape, s1)
        self.assertEqual(hit.point, (29,0))
        self.assertEqual(hit.distance, 1)
        self.assertEqual(hit.gradient, (1,0))

    def testBBQuery(self):
        s = p.Space()

        b1 = p.Body(1,1)
        b1.position = 19,0
        s1 = p.Circle(b1, 10)
        s.add(s1)

        b2 = p.Body(1, 1)
        b2.position = 0, 0
        s2 = p.Circle(b2, 10)
        s.add(s2)

        bb = p.BB(-7, -7, 7, 7)

        hits = s.bb_query(bb, p.ShapeFilter())
        self.assertEqual(len(hits), 1)
        self.assert_(s2 in hits)
        self.assert_(s1 not in hits)

    def testShapeQuery(self):

        b = p.Body()
        s = p.Circle(b, 2)
        b.position = 20,1

        hits = self.s.shape_query(s)
        self.assert_(self.s1 not in hits)
        self.assert_(self.s2 in hits)


    def testStaticPointQueries(self):
        b = p.Body()
        c = p.Circle(b, 10)
        b.position = -50,-50

        self.s.add(c)

        hit = self.s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit.shape, c)

        hits = self.s.point_query( (-50,-55), 0, p.ShapeFilter())
        self.assertEqual(hits[0].shape, c)

    def testReindexShape(self):
        s = p.Space()
        
        b = p.Body()
        c = p.Circle(b, 10)

        s.add(c)

        b.position = -50,-50
        hit = self.s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit, None)
        s.reindex_shape(c)
        hit = s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit.shape, c)
        
    def testReindexShapesForBody(self):
        s = p.Space()
        b = p.Body(body_type=p.Body.STATIC)
        c = p.Circle(b, 10)

        s.add(c)

        b.position = -50,-50
        hit = s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit, None)
        s.reindex_shapes_for_body(b)
        
        hit = s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit.shape, c)

    def testReindexStatic(self):
        s = p.Space()
        b = p.Body(body_type=p.Body.STATIC)
        c = p.Circle(b, 10)

        s.add(c)

        b.position = -50,-50
        hit = s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit, None)
        s.reindex_static()
        hit = s.point_query_nearest( (-50,-55), 0, p.ShapeFilter() )
        self.assertEqual(hit.shape, c)

    def testReindexStaticCollision(self):
        s = p.Space()
        b1 = p.Body(10, 1000)
        c1 = p.Circle(b1, 10)
        b1.position = 20, 20

        b2 = p.Body(body_type=p.Body.STATIC)
        s2 = p.Segment(b2, (-10,0), (10,0),1)

        s.add(b1,c1)
        s.add(s2)

        s2.unsafe_set_b((100,0))
        s.gravity = 0, -100

        for x in range(10):
            s.step(.1)
            
        self.assert_(b1.position.y < 0)

        b1.position = 20,20
        b1.velocity = 0,0
        s.reindex_static()

        for x in range(10):
            self.s.step(.1)

        self.assert_(b1.position.y > 10)

    def testSegmentQuery(self):
        s = p.Space()

        b1 = p.Body(1,1)
        b1.position = 19,0
        s1 = p.Circle(b1, 10)
        s.add(s1)

        b2 = p.Body(1, 1)
        b2.position = 0, 0
        s2 = p.Circle(b2, 10)
        s.add(s2)

        hits = s.segment_query((-13, 0), (131,0), 0, p.ShapeFilter())

        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0].shape, s2)
        self.assertEqual(hits[0].point, (-10,0))
        self.assertEqual(hits[0].normal, (-1,0))
        self.assertAlmostEqual(hits[0].alpha, 0.0208333333333)

        self.assertEqual(hits[1].shape, s1)
        self.assertEqual(hits[1].point, (9,0))
        self.assertEqual(hits[1].normal, (-1,0))
        self.assertAlmostEqual(hits[1].alpha, 0.1527777777777)

        hits = s.segment_query((-13, 50), (131,50), 0, p.ShapeFilter())
        self.assertEqual(len(hits), 0)

    def testSegmentQueryFirst(self):
        s = p.Space()

        b1 = p.Body(1,1)
        b1.position = 19,0
        s1 = p.Circle(b1, 10)
        s.add(s1)

        b2 = p.Body(1, 1)
        b2.position = 0, 0
        s2 = p.Circle(b2, 10)
        s.add(s2)

        hit = s.segment_query_first((-13, 0), (131,0), 0, p.ShapeFilter())

        self.assertEqual(hit.shape, s2)
        self.assertEqual(hit.point, (-10,0))
        self.assertEqual(hit.normal, (-1,0))
        self.assertAlmostEqual(hit.alpha, 0.0208333333333)

        hit = s.segment_query_first((-13, 50), (131,50), 0, p.ShapeFilter())
        self.assertEqual(hit, None)

    def testStaticSegmentQueries(self):
        b = p.Body()
        c = p.Circle(b, 10)
        b.position = -50,-50

        self.s.add(c)

        hit = self.s.segment_query_first( (-70,-50), (-30, -50), 0, p.ShapeFilter() )
        self.assertEqual(hit.shape, c)
        hits = self.s.segment_query( (-70,-50), (-30, -50), 0, p.ShapeFilter() )
        self.assertEqual(hits[0].shape, c)

    def testCollisionHandlerAssignNone(self):
        s = p.Space()

        b1, b2 = p.Body(1, 3), p.Body(10, 100)
        s.add(b1, b2)
        b1.position = 10, 0
        b2.position = 20, 0
        s1, s2 = p.Circle(b1, 5), p.Circle(b2, 10)
        s.add(s1, s2)

        self.hits = 0
        def pre_solve(space, arb):
            print "pre_solve", arb
            self.hits = self.hits + 1
            return True

        h = s.collision_handler(0,0)
        h.pre_solve = pre_solve
        s.step(1)
        self.assertEqual(self.hits, 1)
        h.pre_solve = None
        #h = s.default_collision_handler()
        #h._handler.contents.preSolveFunc = dh._handler.contents.preSolveFunc
        #h._handler.contents.preSolveFunc = h._orig_PreSolveFunc
        s.step(1)
        s.step(1)
        s.step(1)
        s.step(1)
        self.assertEqual(self.hits, 1)

    def testCollisionHandlerBegin(self):
        s = p.Space()

        b1 = p.Body(1, 1)
        c1 = p.Circle(b1, 10)
        b1.position = 0,30

        b2 = p.Body(body_type = p.Body.STATIC)
        c2 = p.Circle(b2, 10)
        b2.position = 0,0

        s.add(b1, c1, b2, c2)
        s.gravity = 0,-100
        self.num_of_begins = 0
        def begin(space, arb):
            self.num_of_begins += 1
            return True

        h = s.collision_handler(0, 0)
        h.begin = begin

        for x in range(10):
            s.step(0.1)

        s.step(0.1)
        self.assertEqual(self.num_of_begins, 1)

    def testCollisionHandlerBeginNoReturn(self):
        if sys.version_info < (2, 6): return
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            def begin(space, arb):
                return

            self.b1.position = self.b2.position
            self.s.collision_handler(0,0).begin = begin
            self.s.step(0.1)
            self.s.step(0.1)

            self.assertEqual(len(w),1)
            self.assertTrue(issubclass(w[-1].category,UserWarning))

    def testCollisionHandlerPreSolve(self):

        self.begin_shapes = None
        self.begin_contacts = None
        self.begin_space = None

        self.s1.collision_type = 1
        self.s2.collision_type = 2

        def pre_solve(space, arb):
            self.begin_shapes = arb.shapes
            self.begin_contacts = arb.contacts
            self.begin_space = space
            return True

        for x in range(100):
            self.s.step(0.1)

        self.s.collision_handler(1,2).pre_solve = pre_solve
        self.s.step(0.1)
        self.assertEqual(self.s1, self.begin_shapes[0])
        self.assertEqual(self.s2, self.begin_shapes[1])
        self.assertEqual(self.begin_space, self.s)

    def testCollisionHandlerPreSolveNoReturn(self):
        if sys.version_info < (2, 6): return
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            def pre_solve(space, arb):
                return

            self.s.collision_handler(0,0).pre_solve = pre_solve
            self.s.step(0.1)

            self.assertEqual(len(w),1)
            self.assertTrue(issubclass(w[-1].category,UserWarning))

    def testCollisionHandlerPostSolve(self):
        self.hit = 0
        def post_solve(space, arb):
            self.hit += 1

        self.s.collision_handler(0,0).post_solve = post_solve
        self.s.step(0.1)
        self.assertEqual(self.hit, 1)

    def testCollisionHandlerSeparate(self):
        s = p.Space()

        b1 = p.Body(1, 1)
        c1 = p.Circle(b1, 10)
        b1.position = 9,11

        b2 = p.Body(body_type = p.Body.STATIC)
        c2 = p.Circle(b2, 10)
        b2.position = 0,0

        s.add(b1, c1, b2, c2)
        s.gravity = 0,-100

        self.separated = False
        def separate(space, arb):
            self.separated = True

        s.collision_handler(0,0).separate = separate

        for x in range(10):
            s.step(0.1)

        self.assert_(self.separated)

    def testWildcardCollisionHandler(self):
        pass

    def testPostStepCallback(self):
        s = p.Space()
        b1, b2 = p.Body(1, 3), p.Body(10, 100)
        s.add(b1, b2)
        b1.position = 10, 0
        b2.position = 20, 0
        s1, s2 = p.Circle(b1, 5), p.Circle(b2, 10)
        s.add(s1, s2)

        self.number_of_calls = 0
        def f(obj, shapes, test_self):
            for shape in shapes:
                s.remove(shape)
            test_self.number_of_calls += 1
        def pre_solve(space, arb):
            print "pre_solve", arb
            space.add_post_step_callback(f, arb.shapes[0], arb.shapes, test_self = self)
            return True

        ch = s.collision_handler(0,0)
        print 1, ch._handler
        #print 2, dir(ch._handler)
        print 3, ch._handler.contents.preSolveFunc

        ch.pre_solve = pre_solve
        dch = s.default_collision_handler()
        #ch._handler.contents.preSolveFunc = dch._handler.contents.preSolveFunc
        print 4, ch._handler.contents.preSolveFunc
        #print 5,dir(ch._handler.contents.preSolveFunc)
        s.step(0.1)
        self.assertEqual(s.shapes, [])
        print "5 number of calls", self.number_of_calls
        s.add(s1, s2)
        s.step(0.1)
        print "6 number of calls", self.number_of_calls
        self.assertEqual(s.shapes, [])
        s.add(s1, s2)
        #ch._handler.contents.preSolveFunc = x.contents
        #ch.pre_solve = None
        ch._handler.contents.preSolveFunc = dch._handler.contents.preSolveFunc
        s.step(0.1)

        self.assertEqual(self.number_of_calls, 2)

####################################################################
if __name__ == "__main__":
    print ("testing pymunk version " + p.version)
    unittest.main()
