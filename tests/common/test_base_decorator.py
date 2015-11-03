import mock
import unittest

from os_code_profiler.common.decorators import \
    Base as BaseDecorator, \
    DecorateNotImplemented


class FakeObject():
    """
    Fake object class to create dummy instances to pass into
    decorators for testing.

    """
    pass


class TestBaseDecorator(unittest.TestCase):
    """
    Tests the base decorator.

    """
    def test_init(self):
        """
        Tests the init method

        """
        sig = '__mumbo_jumbo__'
        dec = BaseDecorator(sig)
        self.assertTrue(dec._signature, sig)

    def test_set_signature(self):
        """
        Tests the _set_signature method

        """
        dec = BaseDecorator('asig')
        expected_sig = '__test_signature__'

        sig = 'test_signature__'
        dec._set_signature(sig)
        self.assertEquals(dec._signature, expected_sig)

        sig = '__test_signature'
        dec._set_signature(sig)
        self.assertEquals(dec._signature, expected_sig)

        sig = 'test_signature'
        dec._set_signature(sig)
        self.assertEquals(dec._signature, expected_sig)

    def test_has_decorated(self):
        """
        A decorator should be able to determine if an object has
        already been decorated.

        """
        sig = '__mumbo_jumbo__'
        dec = BaseDecorator(sig)
        o = FakeObject()
        self.assertFalse(dec._has_decorated(o))
        setattr(o, sig, True)
        self.assertTrue(dec._has_decorated(o))

    def test_set_decorated(self):
        """
        A decorator should be able to mark an object as decorated to
        prevent redecoration in the future.

        """
        sig = '__mumbo_jumbo__'
        dec = BaseDecorator(sig)
        o = FakeObject()
        dec._set_decorated(o)
        self.assertTrue(hasattr(o, sig))

    def test__call__fresh(self):
        """
        Tests the __call__ method on a fresh(undecorated) object.

        """
        dec = BaseDecorator('__mumbo_jumbo__')
        dec._set_decorated = mock.Mock()
        dec._has_decorated = mock.Mock(return_value=False)

        o = FakeObject()
        dec._decorate = mock.Mock(return_value=o)
        config = {}
        dec(o, config)
        dec._set_decorated.assert_called_with(o)
        dec._decorate.assert_called_once_with(o, config)
        dec._has_decorated.assert_called_with(o)

    def test__call__stale(self):
        """
        Tests the __call_method on a stale(decorated) object

        """
        dec = BaseDecorator('__mumbo_jumbo__')
        dec._set_decorated = mock.Mock()
        dec._decorate = mock.Mock()
        dec._has_decorated = mock.Mock(return_value=True)
        o = FakeObject()
        config = {}
        dec(o, config)
        dec._set_decorated.assert_not_called()
        dec._has_decorated.assert_called_with(o)
        dec._decorate.assert_not_called()

    def test_decorate_not_implemented(self):
        """
        Tests that not implemented the _decorate method raises an exception.

        """
        dec = BaseDecorator('__mumbo_jumbo__')
        o = FakeObject()
        config = {}
        with self.assertRaises(DecorateNotImplemented):
            dec(o, config)
