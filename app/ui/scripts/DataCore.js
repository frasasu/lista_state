
export const DataCore = {
    sessionName: "",
    payload: {
        tables: {},
        analysis: {},
        settings: {
            general: {
                defaultSession: 'new',
                autoSave: true,
                autoSaveInterval: 30,
                defaultFolder: '',
                defaultExportFormat: 'csv'
            },
            editor: {
                theme: 'dracula',
                fontSize: 14,
                fontFamily: "'Fira Code', monospace",
                ligatures: true,
                indentation: 'spaces-4',
                autocomplete: true,
                highlightLine: true,
                lineNumbers: true
            },
            appearance: {
                theme: 'dark',
                accentColor: '#4299e1',
                density: 'comfortable',
                showPreviews: true,
                sidebarCollapsed: false
            },
            performance: {
                memoryLimit: 2048,
                dataCache: true,
                cacheSize: 512,
                parallelThreads: 4,
                asyncLoading: true
            }
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
    },

    updateSettingsCategory(category, values) {
        if (!this.payload.settings[category]) {
            this.payload.settings[category] = {};
        }
        this.payload.settings[category] = {
            ...this.payload.settings[category],
            ...values
        };
        this.save();
    }
};