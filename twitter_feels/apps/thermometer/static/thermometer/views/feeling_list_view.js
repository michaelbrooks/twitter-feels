/**
 * Created by mjbrooks on 3/16/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    views.FeelingListView = views.CommonView.extend({

        className: 'feeling-list-view modal fade',

        template: _.template($('#feeling-list-view-template').html()),

        events: {
            'click li': 'feeling_clicked'
        },

        initialize: function(options) {
            this.update = options.update;

            this.listenTo(this.update, 'show-feeling-list', this.show);
            this.listenTo(this.collection, 'change', this.render);
        },

        show: function() {
            this.$el.modal('show');
        },

        feeling_clicked: function(e) {
            this.$el.modal('hide');

            var feeling_id = $(e.target).data('id');
            console.log(feeling_id);
        },

        render: function() {
            this.$el.html(this.template({
                feelings: this.collection.toJSON()
            }));

            this.$el.modal({
                show: false
            })
        }

    });

})(window);