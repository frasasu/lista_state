import { DataCore } from "./DataCore.js";

class AnalysisManager{
    constructor() {
        this.core = DataCore;
        this.currentAnalysisName = null;
        this.editor = document.querySelector(".analysis .left .top #editor");
        this.lineNumbers = document.getElementById('lineNumbers');
        this.list_analysis = document.querySelector(".analysis .left .bottom .under .liste-analysis");
    }

    Init(){
        setTimeout(() => {
            if (this.core.payload.analysis) {
                this.displayListAnalysis();
            }
        }, 300);

         const first_analysis = Object.keys(this.core.payload.analysis)[0];
        if (first_analysis){
                this.displayAnalysis(first_analysis);
                this.currentAnalysisName = first_analysis;
                this.displayListAnalysis();
        }
    }

    shwowAnalysis(me){
        this.saveCurrentAnalysis();
        this.currentAnalysisName = me.innerText;
        this.displayAnalysis(me.innerText);
    }
    displayAnalysis(name){
       const content_analysis = this.core.payload.analysis[name];
       this.editor.value="";
       this.editor.value = content_analysis || "";
       this.updateLineNumbers();
    }

    displayListAnalysis(){
        const names_analysis = Object.keys(this.core.payload.analysis);
        this.list_analysis.innerHTML = "";

        for (let name of names_analysis){
            let div = document.createElement("div");
            div.className= "div";
            div.innerHTML =`<div onclick="analysisManager.shwowAnalysis(this)" ondblclick="analysisManager.deleteAnalysis(this.innerText)">${name}</div>`
            this.list_analysis.appendChild(div);
        }
    }

    updateLineNumbers() {
        const lines = this.editor.value.split('\n').length;
        let lineNumbersHTML = '';
        for (let i = 1; i <= Math.max(lines, 10); i++) {
            lineNumbersHTML += i + '<br>';
        }
        this.lineNumbers.innerHTML = lineNumbersHTML;
    }

    EventListeners() {
        this.updateLineNumbers();

        this.editor.addEventListener('input', () => {
            this.updateLineNumbers();
        });

        this.editor.addEventListener('scroll', () => {
            this.lineNumbers.scrollTop = this.editor.scrollTop;
        });

        document.querySelector(".analysis .left .bottom .box .new").addEventListener("click", (e)=>{
            e.preventDefault();

            document.getElementById("modal-new-analysis").style.display="flex";
        });

        document.querySelector(".analysis .left .bottom .box .delete").addEventListener("click", (e)=>{
            e.preventDefault();

            document.getElementById("modal-delete-analysis").style.display="flex";
        });

        document.querySelector(".modal-delete-analysis .modal-content .btns .cancel").addEventListener("click", (e)=>{
             document.getElementById("modal-delete-analysis").style.display="none";
        });

        document.querySelector(".modal-new-analysis .modal-content .btns .cancel").addEventListener("click", (e)=>{
             document.getElementById("modal-new-analysis").style.display="none";
        });

        document.querySelector(".modal-new-analysis .modal-content .btns .add_new").addEventListener("click", async (e)=>{
             e.preventDefault();


             const name_analysis_new = document.querySelector(".modal-new-analysis .modal-content .input input").value;

             const names_analysis = Object.keys(this.core.payload.analysis);
             if (names_analysis.includes(name_analysis_new)){
                alert(`L'analyse ${name_analysis_new} sest deja faite.`);
                return;
             }

            this.core.payload.analysis[name_analysis_new] = "#Analyse effectuee";
            this.currentAnalysisName = name_analysis_new;
            this.displayAnalysis(this.currentAnalysisName);
            this.displayListAnalysis();
            await this.core.save();
            document.getElementById("modal-new-analysis").style.display="none";
            alert(`Le fichier d'analyse ${name_analysis_new} est sauvegarde avec success.`);
        });

        document.querySelector(".modal-delete-analysis .modal-content .btns .delete").addEventListener("click", async (e)=>{
            e.preventDefault();

            const name_delete = document.querySelector(".modal-delete-analysis .modal-content .input input").value.trim();
            this.deleteAnalysis(name_delete);
        });

        document.addEventListener("keydown", (e)=>{

            if(e.ctrlKey && (e.key === "d" || e.key === "D")){
                e.preventDefault();

                if (this.currentAnalysisName){
                    this.deleteAnalysis(this.currentAnalysisName);
                }
            }
        });
    }

    async deleteAnalysis(name){

        if(!this.core.sessionName){
            alert("Aucune session selectionnee!");
            return;
        }

        const names_analysis = Object.keys(this.core.payload.analysis);

            if(!names_analysis.includes(name)){
                alert(`Le fichier d'analyse ${name} n'existe pas!`);
                return;
            }

            const confirmDelete = confirm(`Êtes-vous sûr de vouloir supprimer l'analyse "${name}" ?\nCette action est irréversible !`);

          if (!confirmDelete) {
             return;
           }

            delete this.core.payload.analysis[name];
            const remainingAnalysis = Object.keys(this.core.payload.analysis);
            this.currentAnalysisName = remainingAnalysis[0] || null;
            this.displayAnalysis(this.currentAnalysisName);
            this.displayListAnalysis();
            await this.core.save();
            document.getElementById("modal-delete-analysis").style.display="none";
            alert(`L'analyse ${name} supprimee avec success!`);
    }

    async saveCurrentAnalysis(){
        if(!this.currentAnalysisName){
            alert(`Aucune analyse selectionnee!`);
            return;
        }

        const content_analysis = this.editor.value;
        this.core.payload.analysis[this.currentAnalysisName] = content_analysis;
        await this.core.save();
    }
}

const analysisManager = new AnalysisManager();
analysisManager.Init();
analysisManager.EventListeners();

window.analysisManager = analysisManager

