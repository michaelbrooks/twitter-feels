(function (win) {

    win.namespace = new win.Namespace();

    var libs = win.namespace.get('libs');

    //Copy global libraries into libs
    win.Logger && (libs.Logger = win.Logger)
    win.Backbone && (libs.Backbone = win.Backbone)


})(window);