(function (win) {

    win.namespace = new win.Namespace();

    if (win.Logger) {
        var libs = win.namespace.get('libs');
        libs.Logger = win.Logger;
    }

})(window);