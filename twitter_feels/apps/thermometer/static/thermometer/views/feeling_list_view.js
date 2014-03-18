/**
 * Created by mjbrooks on 3/16/14.
 */
(function (win) {

    var views = win.namespace.get('thermometer.views');
    var libs = win.namespace.get('libs');

    var logger = libs.Logger.get('thermometer.views.feeling_list_view');

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
            this.update.add_feeling(feeling_id);
        },

        render: function() {
            this.$el.html(this.template({
                feelings: this.collection.toJSON()
            }));

            this.activate_modal();
        },

        activate_modal: function() {
            if (!this.modal_activated) {
                var self = this;
                this.$el.modal({
                    show: false,
                    backdrop: true
                })
                    .on('shown.bs.modal', function() {
                        $(document).on('keydown.thermometer.feeling_list', function(e) {
                            if (e.which == 27) { //escape
                                self.$el.modal('hide');
                            }
                        });
                    })
                    .on('hidden.bs.modal', function() {
                        $(document).off('keydown.thermometer.feeling_list');
                    });
                this.modal_activated = true;
            }
        }

    });

})(window);