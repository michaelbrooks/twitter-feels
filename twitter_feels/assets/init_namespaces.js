(function (win) {

    //Create a shared namespace object
    win.namespace = new win.Namespace();

    //Copy global libraries into libs
    var libs = win.namespace.get('libs');
    win.Logger && (libs.Logger = win.Logger)
    win.Backbone && (libs.Backbone = win.Backbone)


})(window);