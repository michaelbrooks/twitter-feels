/**
 * Tests for assets/init_namespaces
 * Created by mjbrooks on 3/15/14.
 */
(function (win) {

    describe('init_namespaces.js', function() {

        it("should create a global Namespace object", function() {

            expect(win.namespace).toEqual(jasmine.any(win.Namespace));

        });

        it("should add the global Logger to the libs namespace", function() {
            var libs = win.namespace.get('libs');
            expect(libs.Logger).toBe(win.Logger);
        });

        it("should add the global Backbone to the libs namespace", function() {
            var libs = win.namespace.get('libs');
            expect(libs.Backbone).toBe(win.Backbone);
        });
    });

})(window);