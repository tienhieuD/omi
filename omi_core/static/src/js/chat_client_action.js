odoo.define('omi_core.chat_client_action', function (require) {
    "use strict";

    var Widget = require("web.Widget");
    var ChatAction = require('mail.chat_client_action');
    var KanbanRecord = require('web.KanbanRecord');

    var ChatFloatingScreen = Widget.extend({
        template: 'omi_core.chat_floating_screen',

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.model = options.model;
            this.domain = options.domain || [];
            this.channel_id = parent.channel && parent.channel.id;
        },

        willStart: function () {
            var def = this._fetchData(this.model);
            return $.when(this._super.apply(this, arguments), def);
        },

        _fetchData: function (model) {
            var self = this;

            return this._rpc({
                model: model,
                method: 'search_read',
                kwargs: {
                    domain: self.domain,
                    fields: [
                        'name',
                        // For order
                        'amount_total',
                        'confirmation_date',
                        'order_line',
                        'state',
                        // For product
                        'default_code',
                        'qty_available',
                        'list_price',
                        // For note
                        'memo',
                        'color',
                        'stage_id',
                        'tag_ids',
                    ],
                },
                context: {
                    read_x2m_fields: {
                        'order_line': {
                            'fields': ['name', 'product_uom_qty'],
                            'limit': 5,
                        },
                        'tag_ids': {
                            'fields': ['name'],
                        },
                    },
                    channel_id_to_domain: self.channel_id,
                },
            }).then(function (result) {
                self.data = result;
            });
        },

        // Mixin
        productImage: function (product_id) {
            var session = this.getSession();
            return session.url('/web/image', {
                model: "product.template",
                field: "image_small",
                id: product_id,
            });
        },
        getColorClass: function (colorIndex) {
            return KanbanRecord.prototype._getColorClassname(colorIndex);
        },
        getNoteStage: function () {
            var self = this;
            return _.filter(
                _.unique(_.map(self.data, function (elem) {
                    return elem.stage_id[1];
                })),
                function (elem) {
                    return !_.isUndefined(elem);
                }
            );
        },
    });

    ChatAction.include({
        init: function (parent, action, options) {
            this._super.apply(this, arguments);
            this.floating_screen = new ChatFloatingScreen(this, {});
        },
        events: _.extend({}, ChatAction.prototype.events, {
            'click .js_button_list': '_onClickButtonList',
            'click .omi_task_bar a': '_onClickTaskBarButton',
            'click .js_button_new': '_onClickButtonNew',
            'click .js_record_item': '_onClickItem',
            'keyup .js_omi_search': '_onKeyupSearch',
        }),

        openNavigation: function () {
            $('.o_mail_chat .o_mail_chat_content').addClass('omi_shrink_from_the_right');
        },
        closeNavigation: function () {
            $('.o_mail_chat .o_mail_chat_content').removeClass('omi_shrink_from_the_right');
        },

        reloadList: function (options) {
            this.floating_screen.destroy();
            this.floating_screen = new ChatFloatingScreen(this, options);
            this.floating_screen.appendTo($('.omi_floating_screen'));
        },

        _onKeyupSearch: function (e) {

            var value = $(e.currentTarget).val();
            var model = this.floating_screen.model;
            var domain = value ? [
                ['name', 'ilike', value]
            ] : [];
            this.reloadList({
                model: model,
                domain: domain,
            });

        },

        _onClickItem: function (e) {
            e.preventDefault();
            var self = this;
            var res_id = $(e.currentTarget).data('id');
            var model = $(e.currentTarget).data('model');
            this.do_action({
                type: 'ir.actions.act_window',
                res_id: res_id,
                res_model: model,
                views: [
                    [false, 'form']
                ],
                target: 'new',
                context: {},
                flags: {
                    mode: 'readonly',
                },
            }, {
                on_close: function () {
                    self.reloadList({
                        model: model,
                        domain: self.floating_screen.domain,
                    });
                },
            });
        },

        _onClickButtonList: function (e) {
            e.preventDefault();
            var model = $(e.currentTarget).data('model');
            this.openNavigation();
            this.reloadList({
                model: model,
            });
        },
        _onClickTaskBarButton: function (e) {
            e.preventDefault();
            var action = $(e.currentTarget).data('action');
            switch (action) {
            case 'close':
                this.closeNavigation();
                break;
            case 'search':
                var $searchInput = $('.js_omi_search');
                $searchInput.toggle();
                break;
            default:
                this.closeNavigation();
            }
        },
        _onClickButtonNew: function (e) {
            var self = this;
            var model = $(e.currentTarget).data('model');
            var action = $(e.currentTarget).data('action');
            self._rpc({
                route: '/web/action/load',
                params: {
                    action_id: action,
                },
            }).done(function (result) {
                result.context = {
                    channel_to_default: self.channel.id,
                };
                result.target = "new";
                result.views = [
                    [false, 'form'],
                ];
                result.flags = {
                    action_buttons: true,
                    headless: true,
                };
                self.do_action(result, {
                    on_close: function () {
                        self.reloadList({
                            model: model,
                        });
                    },
                });
            });
        },

        // Inherit functions
        _onChannelClicked: function (event) {
            this._super.apply(this, arguments);
            this.reloadList({
                model: this.floating_screen.model,
            });
        },

    });

});
