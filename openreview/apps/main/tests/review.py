from django.contrib.auth.models import AnonymousUser

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from openreview.apps.main.models import review
from openreview.apps.main.models import Review, set_n_votes_cache, ReviewTree
from openreview.apps.tools.testing import create_test_review, create_test_votes, assert_max_queries, list_queries, \
    create_test_paper, create_test_user, create_test_vote, BaseTestCase

__all__ = ["TestReview"]


class TestReview(BaseTestCase):
    def setUp(self):
        self.review = create_test_review()

        create_test_votes(review=self.review, counts={
            -3: 2,
            -1: 2,
            1: 3,
            2: 1
        })

    def test_set_public(self):
        r = Review(anonymous=True, external=True)
        r.set_public()
        self.assertFalse(r.anonymous)
        self.assertFalse(r.external)
        self.assertFalse(r.external)

    def test_set_anonymous(self):
        r = Review(anonymous=False, poster=create_test_user())
        r.set_anonymous()
        self.assertTrue(r.anonymous)
        self.assertFalse(r.external)
        self.assertIsNone(r.poster)

    def test_set_semi_anonymous(self):
        r = Review(anonymous=False, poster=create_test_user())
        r.set_semi_anonymous()
        self.assertIsNotNone(r.poster)
        self.assertTrue(r.anonymous)
        self.assertTrue(r.is_semi_anonymous)
        self.assertFalse(r.external)
        r.poster = None
        self.assertRaises(r.set_semi_anonymous)

    def test_set_external(self):
        r = Review(anonymous=False, external=False)
        r.set_external()
        self.assertTrue(r.external)
        self.assertTrue(r.anonymous)

    def test_bulk_delete(self):
        r1 = create_test_review()
        r2 = create_test_review()

        self.assertFalse(r1.is_deleted, msg="create_test_review() returned deleted review.")
        self.assertFalse(r2.is_deleted, msg="create_test_review() returned deleted review.")

        reviews = Review.objects.filter(id__in=[r1.id, r2.id])
        review.bulk_delete(reviews)
        self.assertFalse(r1.is_deleted, msg="bulk_delete() should not update given reviews")
        self.assertFalse(r2.is_deleted, msg="bulk_delete() should not update given reviews")

        r1, r2 = Review.objects.order_by("id").filter(id__in=[r1.id, r2.id])
        self.assertTrue(r1.is_deleted, msg="bulk_delete() did not update review")
        self.assertTrue(r2.is_deleted, msg="bulk_delete() did not update review")


    def test_n_downvotes(self):
        self.assertEqual(0, create_test_review().n_downvotes)
        self.assertEqual(8, self.review.n_downvotes)

    def test_n_upvotes(self):
        self.assertEqual(0, create_test_review().n_upvotes)
        self.assertEqual(5, self.review.n_upvotes)

    def test_is_semi_anonymous(self):
        r = create_test_review(poster=create_test_user())
        r.anonymous = True
        self.assertTrue(r.is_semi_anonymous, msg="(anonymous=1 and poster != None) => review is semi anonymous")
        r.poster = None
        self.assertFalse(r.is_semi_anonymous, msg="(anonymous=1 and poster is None) => review is not semi anonymous")

    def test_set_n_votes_cache(self):
        review1 = self.review
        self.setUp()
        review2 = self.review

        # 5 queries must be done without caching
        with list_queries(destination=[]) as l:
            self.assertEqual(review1.n_downvotes, 8)
            self.assertEqual(review2.n_downvotes, 8)
            self.assertEqual(review1.n_upvotes, 5)
            self.assertEqual(review2.n_upvotes, 5)
        self.assertEqual(len(l), 4)

        reviews = set(Review.objects.filter(id__in=(review1.id, review2.id)))
        with assert_max_queries(n=2):
            set_n_votes_cache(reviews)

        review1, review2 = reviews
        with assert_max_queries(n=0):
            self.assertEqual(review1.n_downvotes, 8)
            self.assertEqual(review2.n_downvotes, 8)
            self.assertEqual(review1.n_upvotes, 5)
            self.assertEqual(review2.n_upvotes, 5)

    def test_save(self):
        review1 = create_test_review()
        review2 = create_test_review()

        self.assertNotEqual(review1.paper, review2.paper)

        review3 = Review(parent=review1, paper=review2.paper, poster=create_test_user(), text="foo")
        with self.assertRaises(ValueError, msg="review.parent.paper must be review.paper"):
            review3.save()

        r = create_test_review()
        with self.assertRaises(ValueError, msg="Rating must 1 <= r <= 7"):
            r.rating = 8
            r.save()

        # Values [1 <= r <= 7] + [-1] must be accepted
        for rating in tuple(range(1, 8)) + (-1,):
            r.rating = rating
            r.save()

        with self.assertRaises(ValueError, msg="Review.text.strip() cannot be an empty string"):
            r.text = "\t\t\n\r  "
            r.save()

        with self.assertRaises(ValueError, msg="External review must be anonymous"):
            r.anonymous = False
            r.external = True
            r.save()

        with self.assertRaises(ValueError, msg="Non-deleted reviews with poster=None must be anonymous."):
            r.anonymous = False
            r.poster = None
            r.save()

    def test_delete(self):
        review = create_test_review(rating=2, anonymous=False)

        self.assertIsNotNone(review.text)
        self.assertIsNotNone(review.poster)
        self.assertNotEqual(-1, review.rating)

        review.delete()

        self.assertIsNone(review.text)
        self.assertIsNone(review.poster)
        self.assertEqual(-1, review.rating)
        self.assertEqual(True, review.anonymous)

        # Is save() called?
        review = Review.objects.get(id=review.id)
        self.assertIsNone(review.text)
        self.assertIsNone(review.poster)
        self.assertEqual(-1, review.rating)
        self.assertEqual(True, review.anonymous)

    def test_deleted(self):
        review = create_test_review()
        self.assertFalse(review.is_deleted)
        review.delete()
        self.assertTrue(review.is_deleted)

    def test_get_tree(self):
        r1 = create_test_review()

        tree = r1.get_tree(lazy=False)
        self.assertEqual(r1, tree.review)
        self.assertEqual(0, tree.level)
        self.assertEqual([], list(tree.children))

        r2 = create_test_review(parent=r1)
        r3 = create_test_review(parent=r2)
        r1.parent = r3
        # We've created a loop r1 -> r2 -> r3 -> r1
        r1.save()

        # Uses old cache, should not error
        r1.get_tree(lazy=False)

        r1 = Review.objects.get(id=r1.id)

        try:
            r1.get_tree(lazy=False)
        except ValueError as e:
            error_message = "Detected loop: {r1.id} -> {r3.id} -> {r2.id} -> {r1.id}"
            self.assertEqual(str(e), error_message.format(**locals()))
        else:
            self.fail("get_tree() should have raised an error.")

        # If lazy, no loop is detected
        r1.get_tree()

        # Test queries
        r1 = create_test_review()
        r2 = create_test_review(parent=r1)
        r3 = create_test_review(parent=r2)

        r1 = Review.objects.get(id=r1.id)
        r1.cache()

        with assert_max_queries(n=0):
            r1.get_tree(lazy=False)

        self.assertEqual(r1.get_tree(lazy=False), r1.get_tree(lazy=False))
        self.assertNotEqual(r2.get_tree(lazy=False), r1.get_tree(lazy=False))

        self.assertEqual(r2.get_tree(lazy=False), ReviewTree(review=r2, level=0, children=[
            ReviewTree(review=r3, level=1, children=[])
        ]))

    def test_get_tree_size(self):
        paper = create_test_paper()
        top1 = create_test_review(paper=paper)
        top2 = create_test_review(paper=paper)

        self.assertEqual(top1.get_tree_size(), 1)
        self.assertEqual(top2.get_tree_size(), 1)

        child1, child2, child3 = [create_test_review(parent=top1) for i in range(3)]
        create_test_review(paper=paper, parent=child1)

        top1 = Review.objects.select_related("paper").get(id=top1.id)
        self.assertEqual(top1.get_tree_size(), 5)
        self.assertEqual(child1.get_tree_size(), 2)

    def test_get_n_comments(self):
        paper = create_test_paper()
        top1 = create_test_review(paper=paper)
        child1, *_ = [create_test_review(parent=top1) for i in range(3)]
        create_test_review(paper=paper, parent=child1)

        self.assertEqual(top1.n_comments, 4)
        self.assertEqual(child1.n_comments, 1)

        # Should listen to internal cache
        top1._n_comments = 15
        self.assertEqual(top1.n_comments, 15)

    def test_cache_invalidation(self):
        review = create_test_review()
        review_key = make_template_fragment_key("review", [review.paper_id, review.id])

        # Direct call
        cache.delete(review_key)
        self.assertEqual(None, cache.get(review_key))
        cache.set(review_key, "test")
        self.assertEqual("test", cache.get(review_key))
        review._invalidate_template_caches()
        self.assertEqual(None, cache.get(review_key))

        # After calling review.save()
        cache.set(review_key, "test")
        self.assertEqual("test", cache.get(review_key))
        review.save()
        self.assertEqual(None, cache.get(review_key))

        # After calling review.delete()
        cache.set(review_key, "test")
        self.assertEqual("test", cache.get(review_key))
        review.delete()
        self.assertEqual(None, cache.get(review_key))

        # After calling Vote.save()
        vote = create_test_vote(review=review)
        cache.set(review_key, "test")
        self.assertEqual("test", cache.get(review_key))
        vote.save()
        self.assertEqual(None, cache.get(review_key))

        # After calling Vote.delete()
        cache.set(review_key, "test")
        self.assertEqual("test", cache.get(review_key))
        vote.delete()
        self.assertEqual(None, cache.get(review_key))

    def test_cache_ordering(self):
        paper = create_test_paper()

        r1 = create_test_review(paper=paper)
        r2 = create_test_review(paper=paper)
        r3 = create_test_review(paper=paper)
        r4 = create_test_review(parent=r3)
        r5 = create_test_review(parent=r3)

        create_test_votes({1: 5}, r1)
        create_test_votes({1: 6}, r2)
        create_test_votes({-1: 1, 1: 2}, r3)
        create_test_votes({1: 3}, r4)
        create_test_votes({1: 2}, r5)

        c = lambda t: [x.review for x in t.children]
        to_id = lambda t: [x.id for x in t]

        r1.cache(order=True)
        r3 = r1._reviews[r3.id]

        self.assertEqual(list(r1._reviews.values()), [r2, r1, r4, r5, r3])
        self.assertEqual(set(c(r3.get_tree())), {r4, r5})
        self.assertEqual(list(c(r3.get_tree())), [r4, r5])

        r1 = Review.objects.get(id=r1.id)
        r1.cache(order=True, order_reverse=True)
        self.assertEqual(list(r1._reviews.values()), [r3, r5, r4, r1, r2])
        r3 = r1._reviews[r3.id]
        self.assertEqual(set(c(r3.get_tree())), {r4, r5})
        self.assertEqual(to_id(c(r3.get_tree())), [r5.id, r4.id])

    def test_cache(self):
        paper = create_test_paper()
        top1 = create_test_review(paper=paper)
        top2 = create_test_review(paper=paper)

        child1, child2, child3 = [create_test_review(parent=top1) for i in range(3)]
        leaf = create_test_review(paper=paper, parent=child1)

        all = {top1, top2, child1, child2, child3, leaf}

        # We've build the following tree:
        # top1
        # - child1
        # -- leaf
        # - child2
        # - child3
        # top2
        self.assertEqual(set(paper.reviews.all()), all)

        with assert_max_queries(n=1):
            top1.cache()

        with assert_max_queries(n=0):
            top1.cache()

        self.assertEqual(top1._reviews, {
            top1.id: top1, top2.id: top2, child1.id: child1,
            child2.id: child2, child3.id: child3, leaf.id: leaf
        })

        reviews = top1._reviews
        children = top1._reviews_children

        self.assertEqual(set(), set(children[top2.id]))
        self.assertEqual(set(), set(children[leaf.id]))
        self.assertEqual({child1, child2, child3}, set(children[top1.id]))
        self.assertEqual({leaf}, set(children[child1.id]))

        # Extract cached versions of objects
        child1 = reviews[child1.id]
        child2 = reviews[child2.id]
        child3 = reviews[child3.id]
        leaf = reviews[leaf.id]
        top2 = reviews[top2.id]

        all = {top1, top2, child1, child2, child3, leaf}

        self.assertTrue(top1._reviews is top2._reviews is child1._reviews)
        self.assertTrue(child1._reviews is child2._reviews is child3._reviews)
        self.assertTrue(child3._reviews is leaf._reviews)

        with assert_max_queries(n=0):
            for review in all:
                review.paper
                review.parent

        # Test select_related argument
        r = Review.objects.defer('timestamp', 'text').get(id=top1.id)

        with assert_max_queries(n=2):
            # Two queries needed, because it also needs to fetch `paper`
            r.cache(select_related=("poster",))

        with assert_max_queries(n=0):
            r.poster.id

        with assert_max_queries(n=1):
            r.timestamp

        # Test `only` argument
        r = Review.objects.defer('text', 'timestamp').get(id=top1.id)

        with assert_max_queries(n=2):
            r.cache(defer=("timestamp",))

        with assert_max_queries(n=1):
            r.timestamp

        with assert_max_queries(n=0):
            r.text

    def test_can_delete(self):
        r1 = create_test_review()
        u1 = create_test_user()
        anon = AnonymousUser()

        self.assertFalse(r1.can_delete(anon), "Anonymous user can't delete review.")
        self.assertFalse(r1.can_delete(u1), "Non-owner can't delete review.")
        self.assertTrue(r1.can_delete(r1.poster), "Owner can delete review.")
        r1.set_anonymous()
        self.assertFalse(r1.can_delete(u1), "Anonymous reviews can't be deleted.")
        r1 = Review.objects.get(id=r1.id)
        r1.delete()
        self.assertFalse(r1.can_delete(u1), "Deleted reviews can't be deleted.")

    def test_can_change(self):
        # Same as can_delete for now.
        pass
