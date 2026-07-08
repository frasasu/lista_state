
export const DataCore = {
    sessionName: "",
    payload: {
        tables: {},
        analysis: {},
        // 2 réglages simples et faciles à maintenir.
        settings: {
            theme: 'dark',
            editorFontSize: 14
        }
    },

    update(name, data) {
        this.sessionName = name;

        if (data.settings) {
            this.payload = data;
        } else {

            this.payload = {
                ...data,
                settings: this.payload.settings
            };
        }
    },

    async save() {
        await pywebview.api.save_as(this.payload);
    },

    getSettings() {
        return this.payload.settings;
    },

    updateSettings(newSettings) {
        this.payload.settings = {
            ...this.payload.settings,
            ...newSettings
        };
        this.save();
    }
};