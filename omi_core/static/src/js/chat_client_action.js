odoo.define('omi_core.chat_client_action', function (require) {
    "use strict";

    var Widget = require("web.Widget");
    var ChatAction = require('mail.chat_client_action');
    var KanbanRecord = require('web.KanbanRecord');
    var chat_manager = require('mail.chat_manager');

    var ChatStatusBar = Widget.extend({
        template: 'omi_core.chat_status_bar',
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.options = options;
        },
        start: function() {
            this._super.apply(this, arguments);
        },
    });

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
                        // For omi.quick.reply
                        'reply_content',
                        'keyword_ids',
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
                        'keyword_ids': {
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
            this.chat_status_bar = new ChatStatusBar(this, {});
        },
        events: _.extend({}, ChatAction.prototype.events, {
            'click .js_button_list': '_onClickButtonList',
            'click .omi_task_bar a': '_onClickTaskBarButton',
            'click .js_button_new': '_onClickButtonNew',
            'click .js_record_item': '_onClickItem',
            'click .js_channel_status': '_onClickChannelStatus',
            'click .js_button_header': '_onClickButtonHeader',
            'keyup .js_omi_search': '_onKeyupSearch',
        }),

        openNavigation: function () {
            $('.o_mail_chat .o_mail_chat_content').addClass('omi_shrink_from_the_right');
        },
        closeNavigation: function () {
            $('.o_mail_chat .o_mail_chat_content').removeClass('omi_shrink_from_the_right');
        },

        reloadList: function (options) {
            if (_.isUndefined(options.model)) {
                return false;
            }
            this.floating_screen.destroy();
            this.floating_screen = new ChatFloatingScreen(this, options);
            this.floating_screen.appendTo($('.omi_floating_screen'));
        },

        reloadStatusBar: function () {
            this.chat_status_bar.destroy();
            this.chat_status_bar = new ChatStatusBar(this, {status: this.channel.channel_status});
            this.chat_status_bar.appendTo($('.omi_group_button_right'));
        },

        _onClickButtonHeader: function (e) {
            var self = this;
            var target = $(e.currentTarget);
            var model = target.data('model');
            var method = target.data('method');
            var channel_id = this.channel.id;

            this._rpc({
                model: model,
                method: method,
                args: [this.channel.id],
            }).done(function (action) {
                if (!action.res_id) {
                    return false;
                }
                self.do_action(action);
            });

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

        _onClickChannelStatus: function (e) {
            var self = this;
            var new_status = $(e.currentTarget).data('value');

            this._rpc({
                model: 'mail.channel',
                method: 'change_channel_status',
                args: [this.channel.id, new_status],
            }).done(function (res) {
                self.channel_status = new_status;
                $(e.currentTarget).siblings().removeClass('btn-primary disabled');
                $(e.currentTarget).addClass('btn-primary disabled');
            });
        },

        // Inherit functions
        _onChannelClicked: function (event) {
            var self = this;
            this._super.apply(this, arguments);

            if (typeof(this.channel.id) === 'number') {
                this._rpc({
                    model: 'mail.channel',
                    method: 'read',
                    args: [this.channel.id, ['channel_status']],
                }).done(function (res) {
                    self.channel_status = res[0].channel_status;
                    self.reloadStatusBar();
                });
            }

            this.reloadList({
                model: this.floating_screen.model,
            });

        },

    });

    var make_channel = chat_manager.__proto__.make_channel;

    chat_manager.__proto__.make_channel = function (data, options) {
        var res = make_channel(data, options);
        res.channel_status = data.info.channel_status[data.id];
        return res;
    };

    return ChatFloatingScreen;

});
