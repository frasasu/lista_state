
import { DataCore } from "./DataCore.js";

const DEFAULT_SETTINGS = {
    theme: 'dark',
    editorFontSize: 14
};

class SettingsManager {
    constructor() {
        this.core = DataCore;
    }

    init() {
        this.loadSettingsToUI();
        this.setupEventListeners();
        this.applySettings();
    }

    /** Retourne toujours un objet de settings complet (fusion avec les valeurs par défaut). */
    getSettings() {
        return { ...DEFAULT_SETTINGS, ...(this.core.payload.settings || {}) };
    }

    loadSettingsToUI() {
        const settings = this.getSettings();

        document.getElementById('app-theme').value = settings.theme;
        document.getElementById('editor-font-size').value = settings.editorFontSize;
    }

    saveSettingsFromUI() {
        const fontSize = parseInt(document.getElementById('editor-font-size').value, 10);

        this.core.payload.settings = {
            theme: document.getElementById('app-theme').value,
            editorFontSize: Number.isFinite(fontSize) ? fontSize : DEFAULT_SETTINGS.editorFontSize
        };
    }

    async saveSettings() {
        this.saveSettingsFromUI();
        this.applySettings();

        try {
            const result = await this.core.save();
            if (result && result.error) {
                // Le backend a renvoyé une erreur (ex: aucune session ouverte) :
                // on ne doit pas afficher un faux message de succès.
                this.showNotification(`Erreur lors de la sauvegarde : ${result.error}`, 'error');
            } else {
                this.showNotification('Paramètres sauvegardés', 'success');
            }
        } catch (error) {
            this.showNotification('Erreur lors de la sauvegarde', 'error');
        }
    }

    async resetSettings() {
        if (!confirm('Réinitialiser les paramètres ?')) return;

        this.core.payload.settings = { ...DEFAULT_SETTINGS };
        this.loadSettingsToUI();
        this.applySettings();

        try {
            const result = await this.core.save();
            if (result && result.error) {
                this.showNotification(`Erreur lors de la réinitialisation : ${result.error}`, 'error');
            } else {
                this.showNotification('Paramètres réinitialisés', 'info');
            }
        } catch (error) {
            this.showNotification('Erreur lors de la réinitialisation', 'error');
        }
    }

    applySettings() {
        this.applyTheme();
        this.applyEditorFontSize();

        document.dispatchEvent(new CustomEvent('settings-changed', {
            detail: this.getSettings()
        }));
    }

    applyTheme() {
        const settings = this.getSettings();
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = settings.theme === 'dark' || (settings.theme === 'system' && prefersDark);

        document.body.classList.toggle('dark-theme', isDark);
    }

    applyEditorFontSize() {
        const editor = document.getElementById('editor');
        if (!editor) return;

        const settings = this.getSettings();
        editor.style.fontSize = `${settings.editorFontSize}px`;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            const settingsTab = document.getElementById('settings');
            if (e.ctrlKey && e.key === 's' && settingsTab && settingsTab.classList.contains('active')) {
                e.preventDefault();
                this.saveSettings();
            }
        });
    }
}

const settingsManager = new SettingsManager();
export default settingsManager;
