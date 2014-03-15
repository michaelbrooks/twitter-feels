/**
 * Created by mjbrooks on 3/14/14.
 */
(function () {
    describe("A suite is just a function", function() {
        var a;

        it("and so is a spec", function() {
            a = true;

            expect(a).toBe(true);
        });
    });
})();