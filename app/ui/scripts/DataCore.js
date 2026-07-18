
export const DataCore = {
    sessionName: "",
    payload: {
        tables: {},
        analysis: {},
        // 2 réglages simples 
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
        // On retourne le résultat renvoyé par le backend (save_as) afin que les
        // appelants puissent vérifier si la sauvegarde a réellement réussi
        // (le backend renvoie {success:true} ou {error: "..."}).
        return await pywebview.api.save_as(this.payload);
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