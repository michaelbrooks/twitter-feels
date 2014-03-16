/**
 * Tests for assets/libs/namespace/namespace.js
 *
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('libs/namespace/namespace.js', function() {

        it('exposes a global Namespace class', function() {
            expect(win.Namespace).toBeDefined();
        });

        it('can create new namespaces', function() {

            var ns = new win.Namespace();

            var top = ns.get('top');
            expect(top).toEqual({});

        });

        it('accepts existing namespaces', function() {

            var top = {
                foo: {}
            };

            var ns = new win.Namespace(top);
            expect(ns.get('foo')).toBe(top.foo);
        });

        it('retrieves already created namespaces', function() {
            var ns = new win.Namespace();

            expect(ns.get('foo')).toBe(ns.get('foo'));
        });

        it('can create subspaces', function() {

            var ns = new win.Namespace();

            var foo = ns.get('foo');
            var bar = ns.get('foo.bar');

            expect(foo['bar']).toBeDefined();
            expect(bar).toEqual({});
            expect(foo['bar']).toBe(bar);

        });

        it('saves data attached to namespaces', function() {

            var ns = new win.Namespace();

            var foo = ns.get('top.foo');
            foo.value = 5;

            expect(ns.get('top.foo').value).toBe(foo.value);
        })

    });

})(window);