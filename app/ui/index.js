class DataTableManager {
    constructor() {
        this.name_session_selected = "";
        this.datas = {};
        this.currentNameTable = NaN;
        this.grid_table = document.querySelector(".data-table .grid-table");
        this.list_table = document.querySelector(".data-table .list-table");
    }

    async init() {
        window.addEventListener("pywebviewready", async () => {
            const initial = await pywebview.api.initial_data();
            if (initial.length == 2) {
                this.name_session_selected = initial[0];
                this.datas = initial[1];
            }

            if (this.name_session_selected && this.datas) {
                const session_tile = document.querySelectorAll(".session-tile-data");
                session_tile.forEach(tile => {
                    tile.innerHTML = `<div>Session - ${this.name_session_selected}</div>`;
                });

                const first_table = Object.keys(this.datas.tables)[0]
                this.currentNameTable = first_table
                if (first_table){
                    this.displayTable(first_table)
                }
                this.displayListTable();
            }
        });
    }

    switchTab(id) {
        document.querySelectorAll(".nav-item").forEach(nav => {
            nav.classList.remove("active");
        });
        document.querySelectorAll(".tab").forEach(tab => {
            tab.classList.remove("active");
        });
        document.getElementById(id).classList.add("active");
        event.currentTarget.classList.add("active");
    }

    displayTable(name){
    const tableData = this.datas.tables[name];
    const columns = Object.keys(tableData);
    const length_columns = columns.length;

    if (length_columns === 0) return;

    const first_column = columns[0];
    const length_rows = tableData[first_column].length;
    const rows = [];

    for (let i = 0; i < length_rows; i++) {
        let row = [];
        for (let values of Object.values(tableData)) {
            row.push(values[i]);
        }
        rows.push(row);
    }

    this.grid_table.innerHTML = '';
    let table = document.createElement("table");

    let trh = document.createElement("tr");
    for (let i = 0; i < length_columns; i++) {
        let head = document.createElement("th");
        head.textContent = columns[i];
        trh.appendChild(head);
    }
    table.appendChild(trh);


    for (let r = 0; r < length_rows; r++) {
        let row = document.createElement("tr");
        row.className = "cell";
        for (let c = 0; c < length_columns; c++) {
            let cell = document.createElement("td");
            cell.textContent = rows[r][c];
            cell.contentEditable = true;
            row.appendChild(cell);
        }
        table.appendChild(row);
    }

    this.grid_table.appendChild(table);
}

    displayListTable(){
        this.list_table.innerHTML = '';
    for(let name of Object.keys(this.datas.tables)) {
        let list = document.createElement("div");
        list.className = "list-table-item";
        list.innerHTML = `<div onclick="dataManager.OpenModalTableUtils(this)">${name}</div>`;
        this.list_table.appendChild(list);
    }
    }


    ChooseOptionCreateSession() {
        const session_life = document.getElementById("session-life");
        const new_session = document.getElementById("new_session");
        const div_for_session = document.getElementById("div_for_new_session");

        if (session_life.checked === true && new_session.checked === true) {
            const rslt_create_session_alert = document.getElementById("rslt-create-session-option");
            rslt_create_session_alert.style.display = "block";
            rslt_create_session_alert.textContent = "Choose one among of those options plz!";
            setTimeout(() => {
                rslt_create_session_alert.style.display = "none";
            }, 2000);
        } else {
            if (new_session.checked === true) {
                div_for_session.innerHTML = `
                    <div class="new-session">
                    <div class="form">
                        <div class="name-session">Name of new session</div>
                        <input type="text" id="name-session">
                        <div class="path-session" onclick="dataManager.ChoosePathNewSession()">Choose path your session</div>
                    </div>
                    </div>
                `;
            } else if (session_life.checked === true) {
                div_for_session.innerHTML = `
                    <div class="session-life">
                    <div class="form">
                        <div class="path-session" onclick="dataManager.ChoosePathSessionLife()">Choose that session</div>
                    </div>
                    </div>
                `;
            } else {
                const rslt_create_session_alert = document.getElementById("rslt-create-session-option");
                rslt_create_session_alert.style.display = "block";
                rslt_create_session_alert.textContent = "Choose one among of those options plz!";
                setTimeout(() => {
                    rslt_create_session_alert.style.display = "none";
                }, 2000);
            }
        }
    }

    async ChoosePathNewSession() {
        const name = document.getElementById("name-session");
        if (name && name.value) {
            const name_session = await pywebview.api.ChoosePathNewSession(name.value);
            if (name_session[0]) {
                this.name_session_selected = name_session[0];
                this.datas = name_session[1];
                const session_tile = document.querySelectorAll(".session-tile-data");
                session_tile.forEach(tile => {
                    tile.innerHTML = `<div>Session - ${this.name_session_selected}</div>`;
                });

                const first_table = Object.keys(this.datas.tables)[0]
                if (first_table){
                    this.displayTable(first_table)
                }
                this.displayListTable();
            }
        }
    }

    async ChoosePathSessionLife() {
        const name_session = await pywebview.api.open_file_dialog();
        if (name_session[0]) {
            this.name_session_selected = name_session[0];
            this.datas = name_session[1];
            const session_tile = document.querySelectorAll(".session-tile-data");
            session_tile.forEach(tile => {
                tile.innerHTML = `<div>Session - ${this.name_session_selected}</div>`;
            });
                const first_table = Object.keys(this.datas.tables)[0]
                if (first_table){
                    this.displayTable(first_table)
                }
                this.displayListTable();
        }
    }

    OpenModalTableUtils(me) {
        const modal = document.getElementById("modal_table_utils");
        modal.style.display = "flex";

        const title_modal = document.querySelector(".modal_table_utils .modal-content .title");
        const name_ = me?.innerText || "Table inconnue";
        title_modal.innerHTML = `<h2>Table: ${name_}</h2>`;

        this.currentNameTable = name_ !== "Table inconnue" ? name_ : this.currentNameTable;


        if (name_ === "Table inconnue"){
            modal.style.display = "none";
            return
        }

        const table = document.getElementById("grid-table-columns-variables");
        table.innerHTML = "";

        const columns = Object.keys(this.datas.tables[this.currentNameTable])
        const nbColumns = columns.length

        for (let i = 0; i < nbColumns + 1; i++) {
            const div_var = document.createElement("div");
            div_var.className = i === 0 ? "div_var header" : "div_var";
            div_var.textContent = i === 0 ? "Code's variable" : `var ${i}`;
            table.appendChild(div_var);
        }


        for (let i = 0; i < nbColumns + 1; i++) {
            const div_var = document.createElement("div");
            div_var.className = i === 0 ? "div_var header" : "div_var";
            div_var.textContent = i === 0 ? "Name's variable" : columns[i-1];
            div_var.contentEditable = i === 0 ? "false" : "true";
            table.appendChild(div_var);
        }

        table.style.display = "grid";
        table.style.gridTemplateColumns = `repeat(${nbColumns+1}, 300px)`;
    }

   OpenModalAddRow() {
    if (!this.currentNameTable || !this.datas.tables[this.currentNameTable]) {
        alert("Aucune table sélectionnée !");
        return;
    }

    document.querySelector(".modal_add_row").style.display = "flex";
    const div_editable = document.querySelector(".modal_add_row .modal-content .div_editable");

    div_editable.innerHTML = "";

    const columns = Object.keys(this.datas.tables[this.currentNameTable]);
    const nbColumns = columns.length;

    div_editable.style.display = "grid";
    div_editable.style.gridTemplateColumns = `repeat(${nbColumns}, 200px)`;
    div_editable.style.gap = "5px";


    for (let i = 0; i < nbColumns; i++) {
        const header = document.createElement("div");
        header.className = "add_row header";
        header.textContent = columns[i];
        div_editable.appendChild(header);
    }


    for (let i = 0; i < nbColumns; i++) {
        const cell = document.createElement("div");
        cell.className = "add_row value";
        cell.contentEditable = "true";
        cell.textContent = "";
        div_editable.appendChild(cell);
    }
}



    setupEventListeners() {
document.getElementById("submit_add_row").addEventListener("click", async (e) => {
    e.stopPropagation();

    if (!this.currentNameTable || !this.datas.tables[this.currentNameTable]) {
        alert("Aucune table sélectionnée !");
        return;
    }

    const tableData = this.datas.tables[this.currentNameTable];

    const headers = document.querySelectorAll(
        ".modal_add_row .modal-content .div_editable .add_row.header"
    );
    const valuesDiv = document.querySelectorAll(
        ".modal_add_row .modal-content .div_editable .add_row.value"
    );

    const columns_for_added = Array.from(headers).map(h => h.textContent.trim());
    const datas_added_for_row = Array.from(valuesDiv).map(v => v.textContent.trim());

    if (columns_for_added.length !== datas_added_for_row.length) {
        alert("Erreur : nombre de valeurs différent du nombre de colonnes.");
        return;
    }

    if (datas_added_for_row.some(value => value === "")) {
        alert("Veuillez remplir toutes les cellules !");
        return;
    }

    const newRowData = {};

    for (let i = 0; i < columns_for_added.length; i++) {
        newRowData[columns_for_added[i]] = datas_added_for_row[i];
    }

    const columns = Object.keys(tableData);

    for (let column of columns) {

        if (!Array.isArray(tableData[column])) {
            console.error(`Erreur: ${column} n'est pas un tableau`);
            continue;
        }
        const valueToAdd = newRowData[column] !== undefined ? newRowData[column] : "";
        tableData[column].push(valueToAdd);

    }

    const rowCounts = columns.map(col => tableData[col].length);
    const allSameLength = rowCounts.every(count => count === rowCounts[0]);

    if (!allSameLength) {

        const targetLength = Math.max(...rowCounts);
        for (let column of columns) {
            while (tableData[column].length < targetLength) {
                tableData[column].push("");
            }
        }
    }
    this.displayTable(this.currentNameTable);

    await pywebview.api.save_as(this.datas);

    document.getElementById("modal_add_row").style.display = "none";

    const div_editable = document.querySelector(".modal_add_row .modal-content .div_editable");
    const valueCells = div_editable.querySelectorAll(".add_row.value");
    valueCells.forEach(cell => cell.textContent = "");
});



        document.querySelector(".modal_add_row .modal-content .footer .cancel_add_row").addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById("modal_add_row").style.display = "none";
        });

        document.querySelector("#modal_add_column .add_column_new").addEventListener("click", (e) => {
            e.stopPropagation();

            const input = document.getElementById("name_column_new");
            const new_column_added = input.value.trim();

            const Columns = Object.keys(this.datas.tables[this.currentNameTable])
            const nbColumns = Columns.length

            if (new_column_added && this.currentNameTable !== "") {
                let find=false;
                for(let i=0;i<nbColumns;i++){
                         if(Columns[i] === new_column_added){
                            find = true;
                            break;
                         }
                }

                if(find === true){
                 document.getElementById("modal_add_column").style.display = "none";
                 return
                }

                this.datas.tables[this.currentNameTable][new_column_added]=[];

                for (let i = 0; i < this.datas.tables[this.currentNameTable][Columns[0]].length; i++) {
                   this.datas.tables[this.currentNameTable][new_column_added].push("");
                }

                 this.displayTable(this.currentNameTable);
                pywebview.api.save_as(this.datas);
                input.value = "";
                document.getElementById("modal_add_column").style.display = "none";
                document.getElementById("modal_table_utils").style.display = "none";
            }
        });
        document.querySelector("#modal_delete_column .delete_column").addEventListener("click", (e) => {
            e.stopPropagation();

            const input = document.getElementById("name_column_delete");
            const new_column_delete = input.value.trim();

            const Columns = Object.keys(this.datas.tables[this.currentNameTable])
            const nbColumns = Columns.length

            if (new_column_delete && this.currentNameTable !== NaN) {
                let find=false;
                for(let i=0;i<nbColumns;i++){
                         if(Columns[i] === new_column_delete){
                            find = true;
                            break;
                         }
                }

                if(find === false){
                 document.getElementById("modal_delete_column").style.display = "none";
                 return
                }
                delete this.datas.tables[this.currentNameTable][new_column_delete];

                this.displayTable(this.currentNameTable);
                pywebview.api.save_as(this.datas);
                input.value = "";
                document.getElementById("modal_delete_column").style.display = "none";
                document.getElementById("modal_table_utils").style.display = "none";
            }
        });
        document.querySelector(".modal-add-table .modal-content .footer .cancel").addEventListener("click", function(e){
            e.preventDefault();
            document.getElementById("modal-add-table").style.display="none";
        });
        document.querySelector(".modal-delete-table .modal-content .cancel").addEventListener("click", function(){
            document.getElementById("modal-delete-table").style.display="none";
        });

document.querySelector(".modal-delete-table .delete-table-aply").addEventListener("click", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    await this.DeleteTable();
});

document.getElementById("name_table_to_delete").addEventListener("keypress", async (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        await this.DeleteTable();
    }
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        const deleteModal = document.getElementById("modal-delete-table");
        if (deleteModal.style.display === "flex") {
            deleteModal.style.display = "none";
            document.getElementById("name_table_to_delete").value = "";
        }
    }
});
    }

    OpenModalAddColumn() {
        document.getElementById("modal_add_column").style.display = "flex";
    }
    OpenModalDeleteColumn() {
        document.getElementById("modal_delete_column").style.display = "flex";
    }

    SaveChanges() {
    if (!this.currentNameTable || !this.datas.tables[this.currentNameTable]) {
        alert("Aucune table sélectionnée !");
        return;
    }

    const changedDatas = {};
    const divValues = document.querySelectorAll("#grid-table-columns-variables [contenteditable='true']");
    const columnsNames = Array.from(divValues).map(div => div.textContent.trim()).filter(name => name);

    if (columnsNames.length === 0) {
        alert("Aucun nom de colonne valide !");
        return;
    }
    for (let name of columnsNames) {
        changedDatas[name] = [];
    }

    const editableCells = document.querySelectorAll(".data-table .grid-table table td[contenteditable='true']");

    const nbColumns = columnsNames.length;

    if (editableCells.length % nbColumns !== 0) {
        console.error("Nombre de cellules incohérent:", editableCells.length, "colonnes:", nbColumns);
        alert("Erreur de structure du tableau!");
        return;
    }

    const nbRows = editableCells.length / nbColumns;

    for (let rowIndex = 0; rowIndex < nbRows; rowIndex++) {
        for (let colIndex = 0; colIndex < nbColumns; colIndex++) {
            const cellIndex = rowIndex * nbColumns + colIndex;
            const cellValue = editableCells[cellIndex]?.textContent?.trim() || "";
            changedDatas[columnsNames[colIndex]].push(cellValue);
        }
    }

    this.datas.tables[this.currentNameTable] = changedDatas;

    this.displayTable(this.currentNameTable);

    pywebview.api.save_as(this.datas);

    document.getElementById("modal_table_utils").style.display = "none";

    console.log("Changements sauvegardés avec succès !", changedDatas);
}

    switchTabOption(id){
        document.querySelectorAll(".table_added").forEach(tab=>{
            tab.classList.remove("active");
        });
        document.querySelectorAll(".table_option").forEach(tab=>{
            tab.classList.remove("active");
        });
        document.getElementById(id).classList.add("active");
        event.currentTarget.classList.add("active");
    }

    openModalAddTable(){
        document.getElementById("modal-add-table").style.display = "flex";
    }

    openModalDeleteTable(){
        document.getElementById("modal-delete-table").style.display = "flex";
    }

    async CreateNewTable() {

    if (!this.name_session_selected) {
        alert("Aucune session sélectionnée !");
        return;
    }

    const nameInput = document.querySelector(".form-group-new-table .table_name_new");
    const columnsInput = document.querySelector(".form-group-new-table .table_columns_new");

    if (!nameInput || !columnsInput) {
        alert("Champs du formulaire non trouvés !");
        return;
    }

    const tableName = nameInput.value.trim();
    const columnsInputValue = columnsInput.value.trim();


    if (!tableName) {
        alert("Veuillez entrer un nom de table !");
        return;
    }

    if (!columnsInputValue) {
        alert("Veuillez entrer des noms de colonnes (séparés par des virgules) !");
        return;
    }

    const names_columns = columnsInputValue
        .split(",")
        .map(col => col.trim())
        .filter(col => col.length > 0);

    if (names_columns.length === 0) {
        alert("Aucune colonne valide trouvée !");
        return;
    }

    if (this.datas.tables[tableName]) {
        alert(`La table "${tableName}" existe déjà !`);
        return;
    }

    const tableDatas = {};
    const initialRows = 3;
    for (let name_column of names_columns) {
        tableDatas[name_column] = Array(initialRows).fill("");
    }

    this.datas.tables[tableName] = tableDatas;

    await pywebview.api.save_as(this.datas);

    this.currentNameTable = tableName;
    this.displayTable(tableName);
    this.displayListTable();

    nameInput.value = "";
    columnsInput.value = "";

    document.getElementById("modal-add-table").style.display = "none";
}


async DeleteTable() {

    if (!this.name_session_selected) {
        alert("Aucune session sélectionnée !");
        return;
    }

    const tableNameInput = document.getElementById("name_table_to_delete");
    const tableName = tableNameInput?.value.trim();

    if (!tableName) {
        alert("Veuillez entrer un nom de table !");
        return;
    }

    if (!this.datas.tables || !this.datas.tables[tableName]) {
        alert(`La table "${tableName}" n'existe pas !`);
        return;
    }


    const confirmDelete = confirm(`Êtes-vous sûr de vouloir supprimer la table "${tableName}" ?\nCette action est irréversible !`);

    if (!confirmDelete) {
        return;
    }

    try {
        delete this.datas.tables[tableName];
        await pywebview.api.save_as(this.datas);

        this.displayListTable();

        const remainingTables = Object.keys(this.datas.tables);
        if (remainingTables.length > 0) {

            this.currentNameTable = remainingTables[0];
            this.displayTable(this.currentNameTable);
        } else {
            this.currentNameTable = NaN;
            this.grid_table.innerHTML = '<div class="empty-state">Aucune table disponible</div>';
        }

        tableNameInput.value = "";
        document.getElementById("modal-delete-table").style.display = "none";

        const modalUtils = document.getElementById("modal_table_utils");
        if (modalUtils && modalUtils.style.display === "flex") {
            modalUtils.style.display = "none";
        }

        console.log(`Table "${tableName}" supprimée avec succès !`);

        alert(`Table "${tableName}" supprimée avec succès !`);

    } catch (error) {
        console.error("Erreur lors de la suppression de la table :", error);
        alert("Une erreur est survenue lors de la suppression de la table.");
    }
}

}

const dataManager = new DataTableManager();
dataManager.init();
dataManager.setupEventListeners();
