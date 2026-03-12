// settingsManager.js
import { DataCore } from "./DataCore.js";

class SettingsManager {
    constructor() {
        this.core = DataCore;
    }

    init() {
        this.loadSettingsToUI();
        this.setupEventListeners();
        this.applySettings();
        this.startPerformanceMonitoring();
    }

    // Récupérer les settings depuis DataCore
    getSettings() {
        return this.core.payload.settings || this.core.payload.settings;
    }

    // Sauvegarder les settings dans DataCore
    saveSettings() {
        this.saveSettingsFromUI();
        this.core.save();
        this.applySettings();
        this.showNotification('Paramètres sauvegardés', 'success');
    }

    // Charger les settings dans l'UI
    loadSettingsToUI() {
        const settings = this.getSettings();
        
        // Général
        document.getElementById('default-session').value = settings.general?.defaultSession || 'new';
        document.getElementById('auto-save').checked = settings.general?.autoSave ?? true;
        document.getElementById('auto-save-interval').value = settings.general?.autoSaveInterval || 30;
        document.getElementById('default-folder').value = settings.general?.defaultFolder || '';
        document.getElementById('default-export-format').value = settings.general?.defaultExportFormat || 'csv';

        // Éditeur
        document.getElementById('editor-theme').value = settings.editor?.theme || 'dracula';
        document.getElementById('editor-font-size').value = settings.editor?.fontSize || 14;
        document.getElementById('editor-font-family').value = settings.editor?.fontFamily || "'Fira Code', monospace";
        document.getElementById('editor-ligatures').checked = settings.editor?.ligatures ?? true;
        document.getElementById('editor-indentation').value = settings.editor?.indentation || 'spaces-4';
        document.getElementById('editor-autocomplete').checked = settings.editor?.autocomplete ?? true;
        document.getElementById('editor-highlight-line').checked = settings.editor?.highlightLine ?? true;
        document.getElementById('editor-line-numbers').checked = settings.editor?.lineNumbers ?? true;

        // Apparence
        document.getElementById('app-theme').value = settings.appearance?.theme || 'dark';
        document.getElementById('accent-color').value = settings.appearance?.accentColor || '#4299e1';
        document.getElementById('ui-density').value = settings.appearance?.density || 'comfortable';
        document.getElementById('show-previews').checked = settings.appearance?.showPreviews ?? true;
        document.getElementById('sidebar-collapsed').checked = settings.appearance?.sidebarCollapsed || false;

        // Performance
        document.getElementById('memory-limit').value = settings.performance?.memoryLimit || 2048;
        document.getElementById('data-cache').checked = settings.performance?.dataCache ?? true;
        document.getElementById('cache-size').value = settings.performance?.cacheSize || 512;
        document.getElementById('parallel-threads').value = settings.performance?.parallelThreads || 4;
        document.getElementById('async-loading').checked = settings.performance?.asyncLoading ?? true;
    }

    // Sauvegarder les settings depuis l'UI vers DataCore
    saveSettingsFromUI() {
        const settings = {
            general: {
                defaultSession: document.getElementById('default-session').value,
                autoSave: document.getElementById('auto-save').checked,
                autoSaveInterval: parseInt(document.getElementById('auto-save-interval').value),
                defaultFolder: document.getElementById('default-folder').value,
                defaultExportFormat: document.getElementById('default-export-format').value
            },
            editor: {
                theme: document.getElementById('editor-theme').value,
                fontSize: parseInt(document.getElementById('editor-font-size').value),
                fontFamily: document.getElementById('editor-font-family').value,
                ligatures: document.getElementById('editor-ligatures').checked,
                indentation: document.getElementById('editor-indentation').value,
                autocomplete: document.getElementById('editor-autocomplete').checked,
                highlightLine: document.getElementById('editor-highlight-line').checked,
                lineNumbers: document.getElementById('editor-line-numbers').checked
            },
            appearance: {
                theme: document.getElementById('app-theme').value,
                accentColor: document.getElementById('accent-color').value,
                density: document.getElementById('ui-density').value,
                showPreviews: document.getElementById('show-previews').checked,
                sidebarCollapsed: document.getElementById('sidebar-collapsed').checked
            },
            performance: {
                memoryLimit: parseInt(document.getElementById('memory-limit').value),
                dataCache: document.getElementById('data-cache').checked,
                cacheSize: parseInt(document.getElementById('cache-size').value),
                parallelThreads: parseInt(document.getElementById('parallel-threads').value),
                asyncLoading: document.getElementById('async-loading').checked
            }
        };

        this.core.payload.settings = settings;
    }

    // Appliquer les paramètres
    applySettings() {
        this.applyTheme();
        this.applyEditorSettings();
        this.applyAppearanceSettings();
        
        // Notifier les autres modules
        document.dispatchEvent(new CustomEvent('settings-changed', { 
            detail: this.getSettings() 
        }));
    }

    applyTheme() {
        const settings = this.getSettings();
        const theme = settings.appearance?.theme || 'dark';
        const accentColor = settings.appearance?.accentColor || '#4299e1';
        
        document.documentElement.style.setProperty('--accent-color', accentColor);
        
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
    }

    applyEditorSettings() {
        const editor = document.getElementById('editor');
        if (!editor) return;

        const settings = this.getSettings();
        const styles = {
            fontSize: (settings.editor?.fontSize || 14) + 'px',
            fontFamily: settings.editor?.fontFamily || "'Fira Code', monospace",
            fontVariantLigatures: settings.editor?.ligatures ? 'normal' : 'none'
        };

        Object.assign(editor.style, styles);
    }

    // ===== VERSION AVEC ANIMATIONS =====
applyAppearanceSettings() {
    const settings = this.getSettings();
    const density = settings.appearance?.density || 'comfortable';
    const container = document.querySelector('.app-shell');
    const sideLeft = document.querySelector('.side-left');
    
    if (!sideLeft) return;
    
    // Appliquer la densité
    container.classList.remove('density-compact', 'density-spacious');
    if (density !== 'comfortable') {
        container.classList.add(`density-${density}`);
    }

    // Appliquer la réduction de la barre latérale avec animation
    if (settings.appearance?.sidebarCollapsed) {
        // Mode réduit avec icônes seulement
        sideLeft.style.transition = 'width 0.3s ease, padding 0.3s ease';
        sideLeft.style.width = '80px';
        sideLeft.style.padding = '30px 5px';
        
        // Pour chaque élément de navigation
        sideLeft.querySelectorAll('.nav-item').forEach(item => {
            const icon = item.querySelector('.menu-icon');
            const originalText = item.textContent.trim().replace('✓', '').trim();
            
            // Sauvegarder le texte original dans un data attribute
            item.setAttribute('data-original-text', originalText);
            
            // Garder seulement l'icône
            if (icon) {
                item.innerHTML = '';
                item.appendChild(icon);
            }
            
            // Ajouter un tooltip
            item.setAttribute('title', originalText);
            
            // Style pour l'état réduit
            item.style.justifyContent = 'center';
            item.style.padding = '15px 0';
            item.style.margin = '5px 0';
            item.style.borderRadius = '8px';
            
            // Agrandir légèrement l'icône
            if (icon) {
                icon.style.fontSize = '24px';
                icon.style.margin = '0';
            }
        });
        
        // Ajuster le titre principal
        const title = sideLeft.querySelector('.title');
        if (title) {
            title.style.transition = 'all 0.3s ease';
            title.style.fontSize = '24px';
            title.style.padding = '10px 0';
            title.style.marginBottom = '30px';
            title.style.borderBottom = 'none';
            title.innerHTML = '📊';
            title.setAttribute('title', 'Lista State');
            title.style.letterSpacing = '0';
        }
        
        // Cacher le spacer
        const spacer = sideLeft.querySelector('.spacer');
        if (spacer) {
            spacer.style.display = 'none';
        }
        
        // Cacher le texte après l'icône dans le titre de session
        document.querySelectorAll('.session-tile-data').forEach(el => {
            el.setAttribute('data-full-text', el.textContent);
            el.style.fontSize = '12px';
            el.style.justifyContent = 'center';
        });
        
    } else {
        // Mode normal
        sideLeft.style.transition = 'width 0.3s ease, padding 0.3s ease';
        sideLeft.style.width = '280px';
        sideLeft.style.padding = '30px 20px';
        
        // Restaurer les éléments de navigation
        const navTexts = ['Data Editor', 'Data Analysis', 'Session', 'Settings'];
        
        sideLeft.querySelectorAll('.nav-item').forEach((item, index) => {
            const icon = item.querySelector('.menu-icon');
            const originalText = item.getAttribute('data-original-text') || navTexts[index] || '';
            
            // Restaurer l'icône + texte
            if (icon) {
                item.innerHTML = '';
                item.appendChild(icon);
                item.appendChild(document.createTextNode(` ${originalText}`));
                
                // Restaurer la taille de l'icône
                icon.style.fontSize = '20px';
                icon.style.margin = '';
            }
            
            // Enlever le tooltip
            item.removeAttribute('title');
            
            // Restaurer le style
            item.style.justifyContent = 'space-between';
            item.style.padding = '15px 20px';
            item.style.margin = '0';
            item.style.borderRadius = '12px';
        });
        
        // Restaurer le titre
        const title = sideLeft.querySelector('.title');
        if (title) {
            title.style.fontSize = '28px';
            title.style.padding = '';
            title.style.marginBottom = '';
            title.style.borderBottom = '';
            title.innerHTML = 'Lista State';
            title.removeAttribute('title');
            title.style.letterSpacing = '1px';
        }
        
        // Restaurer le spacer
        const spacer = sideLeft.querySelector('.spacer');
        if (spacer) {
            spacer.style.display = 'block';
        }
        
        // Restaurer les titres de session
        document.querySelectorAll('.session-tile-data').forEach(el => {
            const fullText = el.getAttribute('data-full-text') || 'New session';
            el.textContent = fullText;
            el.style.fontSize = '16px';
            el.style.justifyContent = '';
        });
    }
}

    // Changer d'onglet dans les paramètres
    switchSettingsTab(tabId) {
        document.querySelectorAll('.settings-menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.settings-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        event.currentTarget.classList.add('active');
        document.getElementById(`settings-${tabId}`).classList.add('active');
    }

    // Parcourir un dossier
    async browseFolder() {
        if (window.pywebview) {
            const folder = await pywebview.api.choose_folder();
            if (folder) {
                document.getElementById('default-folder').value = folder;
                if (this.getSettings().general?.autoSave) {
                    this.saveSettings();
                }
            }
        }
    }

    // Réinitialiser les paramètres
    resetSettings() {
        if (confirm('Réinitialiser tous les paramètres ?')) {
            this.core.payload.settings = {
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
            };
            this.loadSettingsToUI();
            this.applySettings();
            this.core.save();
            this.showNotification('Paramètres réinitialisés', 'info');
        }
    }

    // Exporter les paramètres
    exportSettings() {
        const settings = this.getSettings();
        const dataStr = JSON.stringify(settings, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = 'lista-settings.json';
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        this.showNotification('Paramètres exportés', 'success');
    }

    // Importer les paramètres
    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    const settings = JSON.parse(e.target.result);
                    this.core.payload.settings = settings;
                    this.loadSettingsToUI();
                    this.applySettings();
                    this.core.save();
                    this.showNotification('Paramètres importés', 'success');
                } catch (error) {
                    this.showNotification('Erreur lors de l\'import', 'error');
                }
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }

    // Vider le cache
    async clearCache() {
        if (confirm('Vider le cache ?')) {
            // Implémentation spécifique à votre application
            this.showNotification('Cache vidé', 'success');
        }
    }

    // Monitorer les performances
    startPerformanceMonitoring() {
        setInterval(() => {
            this.updatePerformanceStats();
        }, 5000);
    }

    updatePerformanceStats() {
        const tables = Object.keys(this.core.payload.tables || {}).length;
        const analyses = Object.keys(this.core.payload.analysis || {}).length;
        
        document.getElementById('memory-usage').textContent = 
            `${Math.round(performance.memory?.usedJSHeapSize / 1048576 || 0)} MB`;
        document.getElementById('loaded-tables').textContent = tables;
        document.getElementById('loaded-analyses').textContent = analyses;
        document.getElementById('last-analysis').textContent = 
            new Date().toLocaleTimeString();
    }

    // Afficher une notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    setupEventListeners() {
        // Auto-sauvegarde quand on change les paramètres
        const autoSaveInputs = document.querySelectorAll('#settings input, #settings select');
        autoSaveInputs.forEach(input => {
            input.addEventListener('change', () => {
                const settings = this.getSettings();
                if (settings.general?.autoSave) {
                    this.saveSettings();
                }
            });
        });

        // Sauvegarde manuelle avec Ctrl+S
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's' && document.getElementById('settings').classList.contains('active')) {
                e.preventDefault();
                this.saveSettings();
            }
        });
    }
}

// Créer et exporter l'instance
const settingsManager = new SettingsManager();
export default settingsManager;