/** @odoo-module **/

/**
 * Fixed version of SpreadsheetCollaborativeChannel that ensures save status
 * only updates after the server confirms data persistence.
 * 
 * This is a complete override of the original class to fix a bug where
 * messages were acknowledged locally before the server confirmed persistence.
 */


export class SpreadsheetCollaborativeChannel {
    static dependencies = ["bus_service", "orm"];
    /**
     * @param {Env} env
     * @param {string} resModel model linked to the spreadsheet
     * @param {number} resId Id of the spreadsheet
     * @param {number} [shareId]
     * @param {string} [accessToken] sharing token
     */
    constructor(env, resModel, resId, shareId, accessToken) {
        this.env = env;
        this.orm = env.services.orm.silent;
        this.resId = resId;
        this.resModel = resModel;
        this.shareId = shareId;
        this.accessToken = accessToken;
        /**
         * A callback function called to handle messages when they are received.
         */
        this._listener;
        /**
         * Messages are queued while there is no listener. They are forwarded
         * once it registers.
         */
        this._queue = [];
        this._channel = this._getChannel();
        this.env.services.bus_service.addChannel(this._channel);
        this.env.services.bus_service.subscribe("spreadsheet", (payload) => {
            if (payload.id === this.resId) {
                this._handleNotification(payload);
            }
        });
    }

    /**
     * Register a function that is called whenever a new spreadsheet revision
     * message notification is received by server.
     *
     * @param {any} id
     * @param {Function} callback
     */
    onNewMessage(id, callback) {
        this._listener = callback;
        for (const message of this._queue) {
            callback(message);
        }
        this._queue = [];
    }

    /**
     * Send a message to the server
     *
     * FIX: Removed premature local notification. The server will broadcast
     * the message back via the bus channel after successfully persisting it.
     * This ensures the save status only updates when data is actually persisted.
     *
     * @param {Object} message
     */
    async sendMessage(message) {
        const isAccepted = await this.orm.call(this.resModel, "dispatch_spreadsheet_message", [
            this.resId,
            message,
            this.accessToken,
        ]);
        // FIX: Do not immediately handle notification locally.
        // The server will broadcast the message back via the bus channel
        // after successfully persisting it. The bus subscription will handle
        // the notification at that point, ensuring the save status only
        // updates when data is actually persisted.
        //
        // Removed: if (isAccepted) { this._handleNotification(message); }
        //
        // If the message is rejected (isAccepted = false), it should not be
        // acknowledged anyway, so we simply don't handle it here.
    }

    /**
     * Stop listening new messages
     */
    leave() {
        this._listener = undefined;
    }

    /**
     * Either forward the message to the listener if it's already registered,
     * or put it in a queue.
     *
     * @private
     * @param {Object} notifs
     */
    _handleNotification(payload) {
        if (!this._listener) {
            this._queue.push(payload);
        } else {
            this._listener(payload);
        }
    }

    /**
     * @private
     * @returns {string}
     */
    _getChannel() {
        // Listening this channel tells the server the spreadsheet is active
        // but the server will actually push to channel [{dbname},  {resModel}, {resId}]
        // The user can listen to this channel only if he has the required read access.
        const channel = `spreadsheet_collaborative_session:${this.resModel}:${this.resId}`;
        if (this.shareId && this.accessToken) {
            return `${channel}:${this.shareId}:${this.accessToken}`;
        }
        return channel;
    }
}
