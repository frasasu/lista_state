INDEX_HTML =r"""

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    color: #2d3748;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 10px;
    transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}

.app-shell {
    display: flex;
    flex: 1;
    overflow: hidden;
    margin: 20px;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    background: #f7fafc;
}

/* ===== SIDE LEFT - MODERNISÉ ===== */
.side-left {
    width: 280px;
    padding: 30px 20px;
    background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    display: flex;
    flex-direction: column;
    gap: 15px;
    box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
}

.side-left .title {
    color: #fff;
    font-size: 28px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 30px;
    letter-spacing: 1px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    position: relative;
    padding-bottom: 15px;
}

.side-left .title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 25%;
    width: 50%;
    height: 3px;
    background: linear-gradient(90deg, #4299e1, #9f7aea);
    border-radius: 3px;
}

.side-left .nav-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    color: #e2e8f0;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 500;
    position: relative;
    overflow: hidden;
}

.side-left .nav-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
}

.side-left .nav-item:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateX(5px);
    color: #fff;
}

.side-left .nav-item:hover::before {
    left: 100%;
}

.side-left .nav-item.active {
    background: linear-gradient(135deg, #4299e1, #667eea);
    border-color: transparent;
    color: white;
    box-shadow: 0 4px 15px rgba(66, 153, 225, 0.4);
}

.side-left .nav-item.active::after {
    content: '✓';
    margin-left: 10px;
    font-weight: bold;
}

.side-left .spacer {
    flex: 1;
}

/* ===== SIDE CENTER - MODERNISÉ ===== */
.side-center {
    flex: 1;
    overflow-y: auto;
    background: #f7fafc;
    padding: 0;
}

.side-center .tab {
    display: none;
    flex-direction: column;
    height: 100%;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.side-center .tab.active {
    display: flex;
}

/* Session Title - Modernisé */
.session-title {
    height: 70px;
    background: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 25px;
    margin: 20px 20px 0;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
}

.session-title .session-tile-data {
    color: #2d3748;
    font-weight: 600;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.session-title .session-tile-data::before {
    content: '📊';
    font-size: 20px;
}

/* Data Table - Modernisé */
.data-table {
    background: white;
    margin: 20px;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    max-width: 100%;
    max-height: 600px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    overflow: hidden;
}

.data-table .grid-table {
    overflow: auto;
    border-radius: 12px;
    border: 1px solid #edf2f7;
}

.data-table .grid-table table {
    border-collapse: collapse;
    width: 100%;
    font-size: 14px;
}

.data-table .grid-table table thead tr {
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    position: sticky;
    top: 0;
    z-index: 10;
}

.data-table .grid-table table th {
    padding: 15px 20px;
    text-align: left;
    font-weight: 600;
    color: #4a5568;
    border-bottom: 2px solid #e2e8f0;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}

.data-table .grid-table table td {
    padding: 12px 20px;
    border-bottom: 1px solid #edf2f7;
    color: #2d3748;
}

.data-table .grid-table table tr:hover td {
    background: #faf5ff;
}

.data-table .grid-table table tr:nth-child(even) {
    background: #fafafa;
}

/* List Table - Modernisé */
.data-table .list-table {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding: 10px 0;
    min-height: 70px;
}

.data-table .list-table .list-table-item {
    padding: 10px 20px;
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    border: 1px solid #e2e8f0;
    border-radius: 30px;
    color: #4a5568;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.data-table .list-table .list-table-item:hover {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(66, 153, 225, 0.3);
}

.data-table .list-table .list-table-item:active {
    transform: translateY(0);
}

/* Utils Table All - Modernisé */
#editor .utils-table-all {
    margin: 20px;
    display: flex;
    gap: 15px;
    justify-content: flex-end;
}

#editor .utils-table-all .add-table-all,
#editor .utils-table-all .delete-table {
    padding: 12px 25px;
    background: white;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 500;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

#editor .utils-table-all .add-table-all::before {
    content: '➕';
    font-size: 14px;
}

#editor .utils-table-all .delete-table::before {
    content: '🗑️';
    font-size: 14px;
}

#editor .utils-table-all .add-table-all:hover {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(72, 187, 120, 0.3);
}

#editor .utils-table-all .delete-table:hover {
    background: linear-gradient(135deg, #f56565, #e53e3e);
    color: white;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(245, 101, 101, 0.3);
}

/* ===== CREATE SESSION SECTION - MODERNISÉ ===== */
.div_create_session {
    margin: 20px;
    border-radius: 20px;
    background: white;
    border: 1px solid #e2e8f0;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.div_create_session .div_title {
    font-size: 18px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.div_create_session .div_title::before {
    content: '🚀';
    font-size: 20px;
}

.div_create_session .btns_create_session {
    background: #f7fafc;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
}

.div_create_session .btns_create_session .form-btn-create-session {
    display: flex;
    gap: 40px;
    justify-content: center;
    margin-bottom: 25px;
}

.div_create_session .btns_create_session .form-group-create-session {
    display: flex;
    align-items: center;
    gap: 10px;
}

.div_create_session .btns_create_session .form-group-create-session label {
    font-weight: 500;
    color: #4a5568;
    cursor: pointer;
}

.div_create_session .btns_create_session .form-group-create-session input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: #4299e1;
}

.div_create_session .btns_create_session .btn-create-session-option {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    padding: 15px 30px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    max-width: 200px;
    margin: 0 auto;
    transition: all 0.2s ease;
    box-shadow: 0 4px 10px rgba(66, 153, 225, 0.3);
}

.div_create_session .btns_create_session .btn-create-session-option:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(66, 153, 225, 0.4);
}

.div_create_session .btns_create_session .btn-create-session-option:active {
    transform: translateY(0);
}

.div_create_session .div_for_new_session {
    background: #f7fafc;
    border-radius: 16px;
    padding: 25px;
    margin-top: 20px;
}

/* New Session Form */
.new-session, .session-life {
    background: white;
    border-radius: 16px;
    padding: 25px;
    border: 1px solid #e2e8f0;
    margin-bottom: 15px;
}

.new-session .form, .session-life .form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.new-session .form .name-session,
.session-life .form .name-session {
    font-size: 14px;
    font-weight: 500;
    color: #4a5568;
    margin-bottom: 5px;
}

.new-session .form input,
.session-life .form input {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 15px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s ease;
    background: white;
}

.new-session .form input:focus,
.session-life .form input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.new-session .form .path-session,
.session-life .form .path-session {
    background: linear-gradient(135deg, #edf2f7, #e2e8f0);
    color: #4a5568;
    padding: 12px 20px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
    border: 1px solid #cbd5e0;
}

.new-session .form .path-session:hover,
.session-life .form .path-session:hover {
    background: linear-gradient(135deg, #e2e8f0, #cbd5e0);
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

/* ===== MODALS - MODERNISÉ ===== */
.modal_table_utils,
.modal_add_row,
.modal_add_column,
.modal_delete_column,
.modal-add-table,
.modal-delete-table,
.modal-new-analysis,
.modal-delete-analysis {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(5px);
    z-index: 2000;
    align-items: center;
    justify-content: center;
    animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
    from { opacity: 0; backdrop-filter: blur(0); }
    to { opacity: 1; backdrop-filter: blur(5px); }
}

.modal-content {
    background: white;
    border-radius: 24px;
    padding: 30px;
    max-width: 90vw;
    max-height: 90vh;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    animation: modalSlideUp 0.4s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes modalSlideUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.modal-content .title {
    font-size: 20px;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.modal-content .title::before {
    content: '📌';
    font-size: 24px;
}

/* Modal Table Utils */
.modal_table_utils .modal-content {
    max-width: 1200px;
    width: 90%;
}

.names_variables {
    overflow: auto;
    margin-bottom: 25px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: white;
}

.grid-table-columns-variables {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px;
    background: #e2e8f0;
}

.div_var {
    background: white;
    padding: 15px;
    text-align: center;
    font-size: 13px;
    color: #2d3748;
    border-bottom: 1px solid #edf2f7;
    min-width: 150px;
}

.div_var.header {
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    font-weight: 700;
    color: #2d3748;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 12px;
    position: sticky;
    top: 0;
    z-index: 10;
}

.div_var.editable:hover {
    background: #ebf8ff;
    cursor: pointer;
}

/* Func Utils */
.func_utils {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
    margin-top: 20px;
}

.func_utils div {
    padding: 12px 20px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    color: #4a5568;
    font-weight: 500;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

.func_utils div::before {
    font-size: 14px;
}

#save_changes_table::before { content: '💾 '; }
#add_row::before { content: '➕ '; }
#add_column::before { content: '📊 '; }
#delete_column::before { content: '🗑️ '; }
.cancel::before { content: '✖️ '; }

.func_utils div:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

#save_changes_table:hover { background: #48bb78; color: white; border-color: #48bb78; }
#add_row:hover { background: #4299e1; color: white; border-color: #4299e1; }
#add_column:hover { background: #9f7aea; color: white; border-color: #9f7aea; }
#delete_column:hover { background: #f56565; color: white; border-color: #f56565; }
.cancel:hover { background: #718096; color: white; border-color: #718096; }

/* Modal Add Row */
.modal_add_row .modal-content {
    width: 600px;
    max-width: 90vw;
}

.div_editable {
    display: grid;
    gap: 10px;
    max-height: 400px;
    overflow: auto;
    margin: 20px 0;
}

.add_row {
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
}

.add_row:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.add_row.header {
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    font-weight: 600;
    color: #2d3748;
}

.submit_add_row {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
    margin: 20px 0;
}

.submit_add_row:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
}

/* Modal Add/Delete Column */
.modal_add_column .modal_content,
.modal_delete_column .modal_content {
    width: 400px;
    background: white;
    border-radius: 24px;
    padding: 30px;
}

.modal_add_column .form,
.modal_delete_column .form {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin: 20px 0;
}

.modal_add_column input,
.modal_delete_column input {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 15px;
    font-size: 14px;
    outline: none;
}

.modal_add_column input:focus,
.modal_delete_column input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.add_column_new,
.delete_column {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
    margin: 20px 0;
}

.add_column_new:hover,
.delete_column:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
}

/* Cancel buttons */
.cancel {
    background: #e2e8f0;
    color: #4a5568;
    padding: 12px 25px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.cancel:hover {
    background: #cbd5e0;
}

/* Modal Add Table */
.modal-add-table .options {
    display: flex;
    gap: 15px;
    margin: 20px 0;
}

.table_added {
    flex: 1;
    padding: 12px;
    background: #f7fafc;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.table_added.active {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border-color: transparent;
}

.table_option {
    display: none;
    animation: fadeIn 0.3s ease;
}

.table_option.active {
    display: block;
}

.form-group-new-table {
    margin-bottom: 20px;
}

.form-group-new-table label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #4a5568;
}

.form-group-new-table input {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 14px;
    outline: none;
}

.form-group-new-table input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.create_new_table,
.import_table {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
}

.create_new_table:hover,
.import_table:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
}

/* Modal Delete Table */
.modal-delete-table .form-group-delete-table {
    margin: 20px 0;
}

.modal-delete-table label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #4a5568;
}

.modal-delete-table input {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 14px;
    outline: none;
}

.modal-delete-table input:focus {
    border-color: #f56565;
    box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.2);
}

.delete-table-aply {
    background: linear-gradient(135deg, #f56565, #e53e3e);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
    margin: 20px 0;
}

.delete-table-aply:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 101, 101, 0.3);
}

/* Modal Analysis */
.modal-new-analysis .input,
.modal-delete-analysis .input {
    margin: 20px 0;
}

.modal-new-analysis input,
.modal-delete-analysis input {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 14px;
    outline: none;
}

.modal-new-analysis input:focus,
.modal-delete-analysis input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.modal-new-analysis .btns,
.modal-delete-analysis .btns {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}

.modal-new-analysis .add_new,
.modal-delete-analysis .delete {
    flex: 1;
    padding: 12px;
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
}

.modal-delete-analysis .delete {
    background: linear-gradient(135deg, #f56565, #e53e3e);
}

.modal-new-analysis .add_new:hover,
.modal-delete-analysis .delete:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px currentColor;
}

/* Settings Tab */
#settings .session-title {
    margin-bottom: 20px;
}

#settings .session-title::before {
    content: '⚙️';
    margin-right: 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .app-shell {
        margin: 10px;
        flex-direction: column;
    }

    .side-left {
        width: 100%;
        padding: 15px;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 10px;
    }

    .side-left .title {
        width: 100%;
        margin-bottom: 10px;
    }

    .side-left .nav-item {
        flex: 1;
        min-width: 120px;
    }

    .side-left .spacer {
        display: none;
    }

    .session-title {
        margin: 10px;
    }

    .data-table {
        margin: 10px;
    }

    .func_utils {
        grid-template-columns: 1fr 1fr;
    }
}

/* Loading States */
.loading {
    position: relative;
    pointer-events: none;
    opacity: 0.7;
}

.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid #4299e1;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Tooltips */
[data-tooltip] {
    position: relative;
    cursor: help;
}

[data-tooltip]:hover::before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 5px 10px;
    background: #2d3748;
    color: white;
    font-size: 12px;
    border-radius: 6px;
    white-space: nowrap;
    z-index: 3000;
    margin-bottom: 5px;
}

@keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* ===== SETTINGS TAB - COMPLET ===== */
.tab#settings {
    height: 100%;
    flex-direction: column;
    padding: 0 20px 20px 20px;
}

/* Le contrôle d'affichage se fait via .tab.active */
.tab.active {
    display: flex;
}

.tab {
    display: none;
}

.settings-container {
    display: flex;
    background: white;
    border-radius: 24px;
    margin: 0 0 20px 0;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
    flex: 1;
    min-height: 500px;
}

/* Sidebar des paramètres */
.settings-sidebar {
    width: 220px;
    background: #f8fafc;
    padding: 20px 0;
    border-right: 1px solid #e2e8f0;
}

.settings-menu-item {
    padding: 15px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #4a5568;
    border-left: 3px solid transparent;
}

.settings-menu-item:hover {
    background: #edf2f7;
}

.settings-menu-item.active {
    background: linear-gradient(90deg, #ebf8ff, white);
    border-left-color: #4299e1;
    color: #2d3748;
    font-weight: 500;
}

.menu-icon {
    font-size: 20px;
    width: 24px;
    text-align: center;
}

/* Contenu des paramètres */
.settings-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    max-height: 600px;
}

.settings-pane {
    display: none;
    animation: fadeIn 0.3s ease;
}

.settings-pane.active {
    display: block;
}

.settings-pane h2 {
    font-size: 24px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 25px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
}

.settings-group {
    background: #f8fafc;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 25px;
    border: 1px solid #edf2f7;
}

.settings-group h3 {
    font-size: 16px;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.settings-group h3::before {
    content: '•';
    color: #4299e1;
    font-size: 20px;
}

.settings-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #edf2f7;
}

.settings-item:last-child {
    border-bottom: none;
}

.settings-item label {
    min-width: 180px;
    font-weight: 500;
    color: #4a5568;
}

.settings-item select,
.settings-item input[type="text"],
.settings-item input[type="number"] {
    padding: 8px 12px;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s ease;
    background: white;
    min-width: 200px;
}

.settings-item select:focus,
.settings-item input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.settings-item input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #4299e1;
}

.setting-description {
    color: #718096;
    font-size: 13px;
    margin-left: 5px;
}

/* Color picker */
.color-picker {
    display: flex;
    align-items: center;
    gap: 10px;
}

.color-picker input[type="color"] {
    width: 50px;
    height: 40px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    padding: 2px;
}

/* Statistiques */
.stats-display {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    padding: 10px;
}

.stats-display div {
    padding: 10px;
    background: white;
    border-radius: 8px;
    border: 1px solid #edf2f7;
    font-size: 14px;
}

.stats-display span {
    font-weight: 600;
    color: #4299e1;
    float: right;
}

/* À propos */
.about-logo {
    text-align: center;
    padding: 30px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}

.app-logo-large {
    font-size: 64px;
    margin-bottom: 10px;
}

.app-name-large {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 5px;
}

.app-version {
    font-size: 16px;
    opacity: 0.9;
}

.about-section {
    margin-bottom: 25px;
}

.about-section h3 {
    font-size: 18px;
    color: #2d3748;
    margin-bottom: 10px;
}

.about-section p {
    color: #4a5568;
    line-height: 1.6;
}

.feature-list {
    list-style: none;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.feature-list li {
    padding: 8px;
    background: #f8fafc;
    border-radius: 8px;
    color: #4a5568;
}

.shortcuts-table {
    width: 100%;
    border-collapse: collapse;
}

.shortcuts-table tr {
    border-bottom: 1px solid #edf2f7;
}

.shortcuts-table td {
    padding: 12px 8px;
}

.shortcuts-table kbd {
    background: #2d3748;
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-family: monospace;
}

/* Actions des paramètres */
.settings-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 0;
    padding: 15px 0;
    border-top: 1px solid #e2e8f0;
}

.settings-btn {
    padding: 10px 20px;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    color: #4a5568;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
}

.settings-btn:hover {
    background: #edf2f7;
    border-color: #cbd5e0;
}

.settings-btn.primary {
    background: linear-gradient(135deg, #4299e1, #3182ce);
    color: white;
    border: none;
}

.settings-btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

/* Thème sombre pour les settings */
.dark-theme .settings-container {
    background: #2d3748;
    border-color: #4a5568;
}

.dark-theme .settings-sidebar {
    background: #1a202c;
    border-right-color: #4a5568;
}

.dark-theme .settings-menu-item {
    color: #cbd5e0;
}

.dark-theme .settings-menu-item:hover {
    background: #2d3748;
}

.dark-theme .settings-menu-item.active {
    background: linear-gradient(90deg, #2d3748, #1a202c);
    color: white;
}

.dark-theme .settings-pane h2 {
    color: #e2e8f0;
    border-bottom-color: #4a5568;
}

.dark-theme .settings-group {
    background: #1a202c;
    border-color: #4a5568;
}

.dark-theme .settings-group h3 {
    color: #e2e8f0;
}

.dark-theme .settings-item {
    border-bottom-color: #4a5568;
}

.dark-theme .settings-item label {
    color: #cbd5e0;
}

.dark-theme .settings-item select,
.dark-theme .settings-item input[type="text"],
.dark-theme .settings-item input[type="number"] {
    background: #2d3748;
    border-color: #4a5568;
    color: white;
}

.dark-theme .setting-description {
    color: #a0aec0;
}

.dark-theme .stats-display div {
    background: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
}

.dark-theme .about-section h3 {
    color: #e2e8f0;
}

.dark-theme .about-section p {
    color: #cbd5e0;
}

.dark-theme .feature-list li {
    background: #2d3748;
    color: #cbd5e0;
}

.dark-theme .shortcuts-table tr {
    border-bottom-color: #4a5568;
}

.dark-theme .shortcuts-table td {
    color: #e2e8f0;
}

.dark-theme .settings-actions {
    border-top-color: #4a5568;
}

.dark-theme .settings-btn {
    background: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
}

.dark-theme .settings-btn:hover {
    background: #4a5568;
}

/* Responsive pour les settings */
@media (max-width: 768px) {
    .settings-container {
        flex-direction: column;
    }
    
    .settings-sidebar {
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        padding: 10px;
        gap: 5px;
    }
    
    .settings-menu-item {
        flex: 1;
        min-width: 120px;
        padding: 10px;
    }
    
    .settings-content {
        max-height: 400px;
    }
    
    .settings-item {
        flex-wrap: wrap;
    }
    
    .settings-item label {
        min-width: 100%;
    }
    
    .stats-display {
        grid-template-columns: 1fr;
    }
    
    .feature-list {
        grid-template-columns: 1fr;
    }
}

/* Améliorations pour la barre latérale réduite */
.side-left {
    transition: width 0.3s ease, padding 0.3s ease;
    overflow: hidden;
}

.side-left .nav-item {
    transition: all 0.2s ease;
    white-space: nowrap;
}

.side-left .nav-item .menu-icon {
    transition: font-size 0.2s ease;
}

/* Tooltip personnalisé pour les icônes */
.side-left .nav-item[title] {
    position: relative;
}

.side-left .nav-item[title]:hover::after {
    content: attr(title);
    position: absolute;
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    background: #2d3748;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    white-space: nowrap;
    margin-left: 10px;
    z-index: 1000;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    animation: tooltipFade 0.2s ease;
}

@keyframes tooltipFade {
    from { opacity: 0; transform: translateY(-50%) translateX(-10px); }
    to { opacity: 1; transform: translateY(-50%) translateX(0); }
}

/* Mode réduit - icônes seulement */
.side-left[style*="width: 80px"] .nav-item {
    text-align: center;
}

.side-left[style*="width: 80px"] .nav-item.active::after {
    content: '';
    position: absolute;
    right: -3px;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 20px;
    background: #4299e1;
    border-radius: 3px 0 0 3px;
}

/* Animation pour le contenu principal quand la barre se réduit */
.side-center {
    transition: margin-left 0.3s ease;
}

/* ===== ANALYSIS SECTION - MODERNISÉ ===== */
.analysis {
    max-width: 1400px;
    height: calc(100vh - 120px);
    min-height: 750px;
    margin: 20px;
    display: flex;
    gap: 20px;
    background: transparent;
}

/* ===== LEFT PANEL - MODERNISÉ ===== */
.analysis .left {
    width: 45%;
    background: white;
    border-radius: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    padding: 20px;
    border: 1px solid rgba(226, 232, 240, 0.6);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.analysis .left:hover {
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}

/* ===== RIGHT PANEL - MODERNISÉ ===== */
.analysis .right {
    flex: 1;
    background: white;
    border-radius: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    padding: 20px;
    border: 1px solid rgba(226, 232, 240, 0.6);
    overflow-y: auto;
    transition: all 0.3s ease;
}

.analysis .right:hover {
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}

/* ===== TOP EDITOR SECTION - MODERNISÉ ===== */
.analysis .left .top {
    flex: 1;
    background: #1a1e2c;
    border-radius: 20px;
    padding: 0;
    overflow: hidden;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    border: 1px solid #2d3748;
    margin-bottom: 20px;
}

.analysis .left .top .editor-wrapper {
    position: relative;
    height: 100%;
    min-height: 450px;
    overflow: auto;
    border-radius: 20px;
    background: #1a1e2c;
}

/* Line Numbers - Modernisé */
.analysis .left .top .editor-wrapper .line-numbers {
    position: absolute;
    left: 0;
    top: 0;
    width: 60px;
    height: 100%;
    background: #0f111a;
    color: #6272a4;
    text-align: right;
    padding: 20px 10px;
    font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    line-height: 1.6;
    user-select: none;
    border-right: 1px solid #2d3748;
    overflow: hidden;
    box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.05);
}

/* Editor Textarea - Modernisé */
.analysis .left .top #editor {
    background: #1a1e2c;
    color: #f8f8f2;
    font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 20px 20px 20px 80px;
    border: none;
    outline: none;
    width: 100%;
    height: 100%;
    min-height: 450px;
    white-space: pre;
    overflow-wrap: normal;
    overflow-x: auto;
    resize: none;
    tab-size: 4;
    caret-color: #ff79c6;
    transition: all 0.2s ease;
}

.analysis .left .top #editor:focus {
    box-shadow: inset 0 0 0 2px #6272a4;
}

/* Syntax Highlighting Colors (pour référence JS) */
.analysis .left .top #editor::selection {
    background: #44475a;
}

/* ===== BOTTOM PANEL - MODERNISÉ ===== */
.analysis .left .bottom {
    height: 250px;
    background: white;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
    border: 1px solid #edf2f7;
    display: flex;
    flex-direction: column;
}

/* Action Buttons Box */
.analysis .left .bottom .box {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    padding: 0 5px;
}

.analysis .left .bottom .box div {
    padding: 12px 25px;
    background: white;
    color: #4a5568;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.analysis .left .bottom .box div::before {
    font-size: 16px;
}

.analysis .left .bottom .box .run::before { content: '▶️ '; }
.analysis .left .bottom .box .new::before { content: '➕ '; }
.analysis .left .bottom .box .delete::before { content: '🗑️ '; }

.analysis .left .bottom .box .run {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    border: none;
    flex: 2;
}

.analysis .left .bottom .box .new {
    background: linear-gradient(135deg, #4299e1, #3182ce);
    color: white;
    border: none;
    flex: 1;
}

.analysis .left .bottom .box .delete {
    background: linear-gradient(135deg, #f56565, #e53e3e);
    color: white;
    border: none;
    flex: 1;
}

.analysis .left .bottom .box div:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.analysis .left .bottom .box div:active {
    transform: translateY(0);
}

/* Under Section - Liste des analyses */
.analysis .left .bottom .under {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #f8fafc;
    border-radius: 16px;
    padding: 15px;
    overflow: hidden;
}

.analysis .left .bottom .under .title {
    color: #2d3748;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.analysis .left .bottom .under .title::before {
    content: '📋';
    font-size: 18px;
}

/* Liste des analyses - Horizontal Scrolling */
.analysis .left .bottom .under .liste-analysis {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 5px 0 15px;
    min-height: 80px;
    scrollbar-width: thin;
    scrollbar-color: #cbd5e0 #f1f5f9;
}

.analysis .left .bottom .under .liste-analysis::-webkit-scrollbar {
    height: 6px;
}

.analysis .left .bottom .under .liste-analysis::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 10px;
}

.analysis .left .bottom .under .liste-analysis::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 10px;
}

.analysis .left .bottom .under .liste-analysis::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

.analysis .left .bottom .under .liste-analysis .div {
    flex-shrink: 0;
}

.analysis .left .bottom .under .liste-analysis .div div {
    padding: 10px 20px;
    background: white;
    color: #4a5568;
    border: 1.5px solid #e2e8f0;
    border-radius: 30px;
    cursor: pointer;
    font-weight: 500;
    font-size: 13px;
    white-space: nowrap;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.analysis .left .bottom .under .liste-analysis .div div:hover {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

/* ===== MODALS - MODERNISÉS ===== */
.modal-new-analysis,
.modal-delete-analysis {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(8px);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 2000;
    animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
    from { opacity: 0; backdrop-filter: blur(0); }
    to { opacity: 1; backdrop-filter: blur(8px); }
}

.modal-new-analysis .modal-content,
.modal-delete-analysis .modal-content {
    width: 450px;
    background: white;
    border-radius: 28px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
    animation: modalSlideUp 0.4s ease;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes modalSlideUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.modal-new-analysis .modal-content .title,
.modal-delete-analysis .modal-content .title {
    height: 70px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}

.modal-new-analysis .modal-content .title::before,
.modal-delete-analysis .modal-content .title::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    100% { left: 100%; }
}

.modal-new-analysis .modal-content .input,
.modal-delete-analysis .modal-content .input {
    margin: 30px 40px;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 5px 15px;
    transition: all 0.2s ease;
    background: #f8fafc;
}

.modal-new-analysis .modal-content .input:focus-within,
.modal-delete-analysis .modal-content .input:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.modal-new-analysis .modal-content .input input,
.modal-delete-analysis .modal-content .input input {
    width: 100%;
    height: 50px;
    border: none;
    outline: none;
    background: transparent;
    color: #2d3748;
    font-size: 16px;
    font-weight: 500;
}

.modal-new-analysis .modal-content .input input::placeholder,
.modal-delete-analysis .modal-content .input input::placeholder {
    color: #a0aec0;
}

.modal-new-analysis .modal-content .btns,
.modal-delete-analysis .modal-content .btns {
    display: flex;
    gap: 15px;
    margin: 30px 40px;
}

.modal-new-analysis .modal-content .btns div,
.modal-delete-analysis .modal-content .btns div {
    flex: 1;
    padding: 14px 20px;
    border-radius: 14px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.modal-new-analysis .modal-content .btns .add_new::before { content: '➕ '; }
.modal-delete-analysis .modal-content .btns .delete::before { content: '🗑️ '; }
.modal-new-analysis .modal-content .btns .cancel::before,
.modal-delete-analysis .modal-content .btns .cancel::before { content: '✖️ '; }

.modal-new-analysis .modal-content .btns .add_new {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    border: none;
}

.modal-delete-analysis .modal-content .btns .delete {
    background: linear-gradient(135deg, #f56565, #e53e3e);
    color: white;
    border: none;
}

.modal-new-analysis .modal-content .btns .cancel,
.modal-delete-analysis .modal-content .btns .cancel {
    background: #e2e8f0;
    color: #4a5568;
    border: none;
}

.modal-new-analysis .modal-content .btns div:hover,
.modal-delete-analysis .modal-content .btns div:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.modal-new-analysis .modal-content .btns div:active,
.modal-delete-analysis .modal-content .btns div:active {
    transform: translateY(0);
}

/* ===== RESULTS SECTION ===== */
.analysis .right {
    padding: 25px;
    background: #f8fafc;
}

.evaluator-results {
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.results-section {
    background: white;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.03);
    border: 1px solid #edf2f7;
    transition: all 0.2s ease;
}

.results-section:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #edf2f7;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-title::before {
    font-size: 20px;
}

.error-section .section-title::before { content: '❌ '; }
.table-section .section-title::before { content: '📊 '; }
.analysis-section .section-title::before { content: '📈 '; }
.info-section .section-title::before { content: 'ℹ️ '; }
.describe-section .section-title::before { content: '📊 '; }
.describe-all-section .section-title::before { content: '📈 '; }
.summary-section .section-title::before { content: '📋 '; }




/* Grille de cartes statistiques */
.stats-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
    margin-top: 15px;
}

.stats-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #edf2f7;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.stats-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stats-card-header {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stats-card.numeric .stats-card-header {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
}

.stats-card.categorical .stats-card-header {
    background: linear-gradient(135deg, #9f7aea, #805ad5);
    color: white;
}

.stats-card-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

.stats-card-header .col-type {
    font-size: 12px;
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 10px;
    border-radius: 20px;
    white-space: nowrap;
}

.stats-card-body {
    padding: 20px;
    background: #fafafa;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #edf2f7;
}

.stat-row:last-child {
    border-bottom: none;
}

.stat-label {
    color: #718096;
    font-size: 13px;
    font-weight: 500;
}

.stat-value {
    font-family: 'Fira Code', monospace;
    font-weight: 600;
    color: #2d3748;
    font-size: 14px;
}

.stats-card.numeric .stat-value {
    color: #48bb78;
}

.stats-card.categorical .stat-value {
    color: #9f7aea;
}

/* Section Statistiques avancées */
.stats-section .section-title::before {
    content: '📊 ';
}

.stats-card {
    border: 1px solid #edf2f7;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    background: white;
}

.stats-header {
    background: linear-gradient(135deg, #48BB78, #38A169);
    color: white;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stats-name {
    font-weight: 600;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.stats-name::before {
    content: '🔬';
}

.stats-target {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 30px;
    font-size: 12px;
}

.stats-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
    padding: 20px;
    background: #f8fafc;
}

.stats-result-item {
    background: white;
    padding: 12px 15px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
    border: 1px solid #edf2f7;
}

.stats-result-item .result-key {
    color: #2d3748;
    font-weight: 600;
    font-size: 13px;
    margin-right: 8px;
}

.stats-result-item .result-value {
    color: #48BB78;
    font-weight: 500;
    font-family: 'Fira Code', monospace;
}


/* Animation pour les nouveaux résultats */
@keyframes slideInStats {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stats-card {
    animation: slideInStats 0.3s ease;
}

/* Barre d'informations */
.info-bar {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    padding: 15px;
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    border-radius: 12px;
    flex-wrap: wrap;
}

.info-badge {
    padding: 6px 14px;
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 5px rgba(66, 153, 225, 0.3);
}

/* Onglets pour statistiques complètes */
.stats-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    padding: 0 5px;
}

.stats-tab {
    padding: 10px 25px;
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 30px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    color: #4a5568;
    transition: all 0.2s ease;
}

.stats-tab:hover {
    background: #f7fafc;
    border-color: #4299e1;
    color: #4299e1;
}

.stats-tab.active {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 10px rgba(66, 153, 225, 0.3);
}

.stats-content {
    display: none;
}

.stats-content.active {
    display: block;
}

/* Grille de résumé */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 25px;
}

.summary-card {
    background: linear-gradient(135deg, #f7fafc, #ffffff);
    border-radius: 16px;
    padding: 25px 20px;
    text-align: center;
    border: 1px solid #edf2f7;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.summary-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    border-color: #4299e1;
}

.summary-value {
    font-size: 32px;
    font-weight: 700;
    color: #4299e1;
    margin-bottom: 8px;
    line-height: 1.2;
}

.summary-label {
    font-size: 14px;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}

/* Liste des colonnes */
.columns-list {
    margin-top: 20px;
    padding: 20px;
    background: #f7fafc;
    border-radius: 16px;
    border: 1px solid #edf2f7;
}

.columns-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 15px;
    color: #2d3748;
    display: flex;
    align-items: center;
    gap: 8px;
}

.columns-title::before {
    content: '📋';
}

.columns-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.column-tag {
    background: white;
    color: #4a5568;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 13px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
    cursor: default;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.column-tag:hover {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(66, 153, 225, 0.3);
}

/* Messages vides */
.empty-message {
    text-align: center;
    padding: 40px 20px;
    color: #a0aec0;
    font-style: italic;
    font-size: 15px;
    background: #f7fafc;
    border-radius: 16px;
    border: 2px dashed #e2e8f0;
}

/* Table Cards */
.table-card {
    border: 1px solid #edf2f7;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    transition: all 0.2s ease;
}

.table-card:hover {
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.table-header {
    background: linear-gradient(135deg, #1a202c, #2d3748);
    color: white;
    padding: 15px 20px;
}

.table-name {
    font-weight: 600;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.table-name::before {
    content: '📋';
}

.table-dimensions {
    background: rgba(255, 255, 255, 0.1);
    padding: 4px 12px;
    border-radius: 30px;
    font-size: 13px;
}

.table-wrapper {
    border: 1px solid #edf2f7;
    border-radius: 12px;
    margin: 15px;
    overflow: auto;
    max-height: 300px;
}

.data-preview {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
}

.data-preview th {
    background: #f7fafc;
    padding: 12px 15px;
    font-weight: 600;
    color: #4a5568;
    border-bottom: 2px solid #e2e8f0;
    position: sticky;
    top: 0;
    z-index: 10;
    white-space: nowrap;
}

.data-preview td {
    padding: 10px 15px;
    border-bottom: 1px solid #edf2f7;
    color: #2d3748;
}

.data-preview tbody tr:hover td {
    background: #faf5ff;
}

.row-index {
    background: #f7fafc;
    font-weight: 600;
    color: #718096;
    width: 50px;
    text-align: center;
}

/* Analysis Cards */
.analysis-card {
    border: 1px solid #edf2f7;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
}

.analysis-header {
    background: linear-gradient(135deg, #4299e1, #667eea);
    color: white;
    padding: 15px 20px;
}

.analysis-name {
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}

.analysis-name::before {
    content: '📊';
}

.analysis-target {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 30px;
    font-size: 12px;
}

.analysis-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    padding: 20px;
    background: #f8fafc;
}

.analysis-result-item {
    background: white;
    padding: 12px 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    border: 1px solid #edf2f7;
    transition: all 0.2s ease;
}

.analysis-result-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    border-color: #cbd5e0;
}

.result-key {
    color: #718096;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
    display: block;
}

.result-value {
    color: #2d3748;
    font-weight: 600;
    font-size: 16px;
}

/* Error Cards */
.error-card {
    background: #fff5f5;
    border-left: 4px solid #f56565;
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.error-line {
    color: #718096;
    font-size: 12px;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 5px;
}

.error-line::before {
    content: '📍';
}

.error-message {
    color: #c53030;
    font-family: 'Fira Code', monospace;
    font-size: 13px;
}

/* Info Cards */
.info-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 8px;
    animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
    from { transform: translateX(-10px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.info-card.success {
    background: #f0fff4;
    color: #22543d;
    border-left: 4px solid #48bb78;
}

.info-card.info {
    background: #ebf8ff;
    color: #1e4b6a;
    border-left: 4px solid #4299e1;
}

.info-icon {
    font-size: 20px;
}

.info-message {
    flex: 1;
    font-weight: 500;
}

.info-line {
    background: rgba(0, 0, 0, 0.05);
    padding: 3px 10px;
    border-radius: 30px;
    font-size: 11px;
}

/* No Results */
.no-results {
    text-align: center;
    color: #a0aec0;
    padding: 60px 20px;
    background: white;
    border-radius: 16px;
    font-size: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.no-results::before {
    content: '📭';
    font-size: 48px;
    opacity: 0.5;
}

/* Loading States */
.loading {
    position: relative;
    pointer-events: none;
    opacity: 0.7;
}

.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 30px;
    height: 30px;
    margin: -15px 0 0 -15px;
    border: 3px solid #4299e1;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== NOUVEAUX STYLES POUR SVG ===== */

.svg-section .section-title::before {
    content: '📈 ';
}

.svg-card {
    border: 1px solid #edf2f7;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    background: white;
}

.svg-header {
    background: linear-gradient(135deg, #9f7aea, #805ad5);
    color: white;
    padding: 12px 20px;
}

.svg-title {
    font-weight: 600;
    font-size: 15px;
}

.svg-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #fafafa;
    min-height: 300px;
}

.svg-container svg {
    max-width: 100%;
    height: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.svg-controls {
    display: flex;
    gap: 8px;
    padding: 10px 15px;
    background: #f8fafc;
    border-top: 1px solid #edf2f7;
}

.svg-controls button {
    padding: 6px 12px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #4a5568;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 4px;
}

.svg-controls button:hover {
    background: #805ad5;
    color: white;
    border-color: #805ad5;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(128, 90, 213, 0.2);
}

/* Mode plein écran pour SVG */
.svg-container:fullscreen {
    padding: 40px;
    background: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.svg-container:fullscreen svg {
    max-width: 90vw;
    max-height: 90vh;
}

/* Bouton de sortie du plein écran */
.fullscreen-exit-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 10px 20px;
    background: #f56565;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
}

.fullscreen-exit-btn:hover {
    background: #e53e3e;
    transform: scale(1.05);
}

/* Animations */
@keyframes slideInStats {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stats-card {
    animation: slideInStats 0.3s ease;
}

.svg-card {
    animation: slideInStats 0.4s ease;
}

/* Responsive */
@media (max-width: 1024px) {
    .analysis {
        flex-direction: column;
        height: auto;
        margin: 10px;
    }

    .analysis .left,
    .analysis .right {
        width: 100%;
    }

    .analysis .left .top .editor-wrapper {
        min-height: 350px;
    }

    .analysis .left .top #editor {
        min-height: 350px;
    }

    .analysis .left .bottom .box {
        flex-wrap: wrap;
    }

    .analysis .left .bottom .box div {
        flex: 1 1 auto;
    }

    .stats-cards-grid {
        grid-template-columns: 1fr;
    }

    .summary-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .stats-tabs {
        flex-direction: column;
        gap: 5px;
    }

    .stats-tab {
        text-align: center;
    }
}

@media (max-width: 640px) {
    .summary-grid {
        grid-template-columns: 1fr;
    }

    .info-bar {
        flex-direction: column;
        gap: 10px;
    }

    .info-badge {
        width: 100%;
        justify-content: center;
    }

    .svg-controls {
        flex-wrap: wrap;
    }

    .svg-controls button {
        flex: 1 1 auto;
    }
}

/* Tooltips */
[data-tooltip] {
    position: relative;
}

[data-tooltip]:hover::before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 6px 12px;
    background: #2d3748;
    color: white;
    font-size: 12px;
    border-radius: 8px;
    white-space: nowrap;
    z-index: 3000;
    margin-bottom: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* Print Styles */
@media print {
    .analysis .left,
    .analysis .bottom,
    .modal-new-analysis,
    .modal-delete-analysis {
        display: none;
    }

    .analysis .right {
        width: 100%;
        box-shadow: none;
    }

    .stats-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}
    </style>
    <title>Lista State</title>
</head>
<body>
<div class="app-shell">
    <div class="side-left">
        <div class="title">Lista State</div>
        <div class="nav-item active" onclick="dataManager.switchTab('editor')">Data Editor</div>
        <div class="nav-item " onclick="dataManager.switchTab('session')">Data Analysis</div>
        <div class="nav-item " onclick="dataManager.switchTab('analysis')">Session</div>
        <div  class="spacer"></div>
        <div class="nav-item " onclick="dataManager.switchTab('settings')">Settings</div>
    </div>
    <div  class="side-center">
        <div id="editor" class="tab active">
            <div class="session-title">
                <div id="session-tile-data" class="session-tile-data">New session</div>
            </div>
            <div class="data-table">
                <div class="grid-table"></div>
                <div class="list-table"></div>
            </div>
            <div class="utils-table-all">
                <div class="add-table-all" onclick="dataManager.openModalAddTable()">Add table</div>
                <div class="delete-table" onclick="dataManager.openModalDeleteTable()">Delete table</div>
            </div>
        </div>
        <div id="analysis" class="tab">
            <div class="session-title">
                <div id="session-tile-data" class="session-tile-data">New session</div>
            </div>
            <div class="div_create_session">
                <div class="div_title">Create Session</div>
                <div class="btns_create_session">
                    <div class="form-btn-create-session">
                        <div class="form-group-create-session">
                            <label>Create new session</label>
                            <input type="checkbox"  id="new_session">
                        </div>
                        <div class="form-group-create-session">
                            <label>Import session</label>
                            <input type="checkbox" id="session-life">
                        </div>
                    </div>
                    <div class="btn-create-session-option" onclick="dataManager.ChooseOptionCreateSession()">Active</div>
                    <div class="rslt-create-session-option" id="rslt-create-session-option"></div>
                </div>
                <div class="div_for_new_session" id="div_for_new_session">Choisir l'option</div>
            </div>
        </div>
        <div id="session" class="tab">
            <div class="session-title">
                <div id="session-tile-data" class="session-tile-data">New session</div>
            </div>
            <div class="analysis">
                <div class="left">
                    <div class="top">
                         <div class="editor-wrapper">
                             <div class="line-numbers" id="lineNumbers">
                                   1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10
                             </div>
                             <textarea id="editor" placeholder="Commencez à taper votre code ici...." spellcheck="false"></textarea>
                          </div>
                    </div>
                    <div class="bottom">
                        <div class="box">
                            <div class="run">Run</div>
                            <div class="new">New</div>
                            <div class="delete">Delete</div>
                        </div>
                        <div class="under">
                            <div class="title" >Liste des analyses</div>
                            <div class="liste-analysis"></div>
                        </div>
                    </div>
                </div>
                <div class="right"></div>
            </div>
        </div>
    <div id="settings" class="tab">
    <div class="session-title">
        <div id="session-tile-data" class="session-tile-data">New session</div>
    </div>
    <div class="settings-container">
        <div class="settings-sidebar">
            <div class="settings-menu-item active" onclick="settingsManager.switchSettingsTab('general')">
                <span class="menu-icon">⚙️</span> Général
            </div>
            <div class="settings-menu-item" onclick="settingsManager.switchSettingsTab('editor')">
                <span class="menu-icon">📝</span> Éditeur
            </div>
            <div class="settings-menu-item" onclick="settingsManager.switchSettingsTab('appearance')">
                <span class="menu-icon">🎨</span> Apparence
            </div>
            <div class="settings-menu-item" onclick="settingsManager.switchSettingsTab('performance')">
                <span class="menu-icon">⚡</span> Performance
            </div>
            <div class="settings-menu-item" onclick="settingsManager.switchSettingsTab('about')">
                <span class="menu-icon">ℹ️</span> À propos
            </div>
        </div>
        <div class="settings-content">
            <div id="settings-general" class="settings-pane active">
                <h2>Paramètres généraux</h2>
                <div class="settings-group">
                    <h3>Session</h3>
                    <div class="settings-item">
                        <label>Session par défaut au démarrage</label>
                        <select id="default-session">
                            <option value="new">Nouvelle session</option>
                            <option value="last">Dernière session ouverte</option>
                            <option value="none">Aucune</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Sauvegarde automatique</label>
                        <input type="checkbox" id="auto-save" checked>
                        <span class="setting-description">Sauvegarder automatiquement les modifications</span>
                    </div>
                    <div class="settings-item">
                        <label>Intervalle de sauvegarde (secondes)</label>
                        <input type="number" id="auto-save-interval" min="5" max="300" value="30">
                    </div>
                </div>
                <div class="settings-group">
                    <h3>Fichiers</h3>
                    <div class="settings-item">
                        <label>Dossier par défaut</label>
                        <input type="text" id="default-folder" placeholder="C:\Users\...">
                        <button class="settings-btn" onclick="settingsManager.browseFolder()">Parcourir</button>
                    </div>
                    <div class="settings-item">
                        <label>Format d'export par défaut</label>
                        <select id="default-export-format">
                            <option value="csv">CSV</option>
                            <option value="json">JSON</option>
                            <option value="excel">Excel</option>
                            <option value="html">HTML</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="settings-editor" class="settings-pane">
                <h2>Paramètres de l'éditeur</h2>
                <div class="settings-group">
                    <h3>Apparence de l'éditeur</h3>
                    <div class="settings-item">
                        <label>Thème</label>
                        <select id="editor-theme">
                            <option value="dracula">Dracula (sombre)</option>
                            <option value="monokai">Monokai</option>
                            <option value="github">GitHub (clair)</option>
                            <option value="solarized">Solarized</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Taille de la police</label>
                        <input type="number" id="editor-font-size" min="10" max="24" value="14">
                    </div>
                    <div class="settings-item">
                        <label>Famille de police</label>
                        <select id="editor-font-family">
                            <option value="'Fira Code', monospace">Fira Code</option>
                            <option value="'Consolas', monospace">Consolas</option>
                            <option value="'Monaco', monospace">Monaco</option>
                            <option value="'Courier New', monospace">Courier New</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Ligatures</label>
                        <input type="checkbox" id="editor-ligatures" checked>
                    </div>
                </div>

                <div class="settings-group">
                    <h3>Comportement</h3>
                    <div class="settings-item">
                        <label>Indentation</label>
                        <select id="editor-indentation">
                            <option value="spaces-2">2 espaces</option>
                            <option value="spaces-4" selected>4 espaces</option>
                            <option value="tab">Tabulation</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Auto-complétion</label>
                        <input type="checkbox" id="editor-autocomplete" checked>
                    </div>
                    <div class="settings-item">
                        <label>Surlignage de la ligne courante</label>
                        <input type="checkbox" id="editor-highlight-line" checked>
                    </div>
                    <div class="settings-item">
                        <label>Numéros de ligne</label>
                        <input type="checkbox" id="editor-line-numbers" checked>
                    </div>
                </div>
            </div>
            <div id="settings-appearance" class="settings-pane">
                <h2>Apparence de l'application</h2>
                <div class="settings-group">
                    <h3>Thème</h3>
                    <div class="settings-item">
                        <label>Thème de l'application</label>
                        <select id="app-theme">
                            <option value="light">Clair</option>
                            <option value="dark" selected>Sombre</option>
                            <option value="system">Système</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Couleur d'accentuation</label>
                        <div class="color-picker">
                            <input type="color" id="accent-color" value="#4299e1">
                        </div>
                    </div>
                </div>
                <div class="settings-group">
                    <h3>Disposition</h3>
                    <div class="settings-item">
                        <label>Densité d'affichage</label>
                        <select id="ui-density">
                            <option value="compact">Compact</option>
                            <option value="comfortable" selected>Confortable</option>
                            <option value="spacious">Espacé</option>
                        </select>
                    </div>
                    <div class="settings-item">
                        <label>Afficher les aperçus</label>
                        <input type="checkbox" id="show-previews" checked>
                    </div>
                    <div class="settings-item">
                        <label>Barre latérale réduite par défaut</label>
                        <input type="checkbox" id="sidebar-collapsed">
                    </div>
                </div>
            </div>
            <div id="settings-performance" class="settings-pane">
                <h2>Performance</h2>
                <div class="settings-group">
                    <h3>Mémoire</h3>
                    <div class="settings-item">
                        <label>Limite de mémoire (Mo)</label>
                        <input type="number" id="memory-limit" min="512" max="16384" value="2048">
                    </div>
                    <div class="settings-item">
                        <label>Cache des données</label>
                        <input type="checkbox" id="data-cache" checked>
                    </div>
                    <div class="settings-item">
                        <label>Taille du cache (Mo)</label>
                        <input type="number" id="cache-size" min="100" max="4096" value="512">
                    </div>
                </div>
                <div class="settings-group">
                    <h3>Traitement</h3>
                    <div class="settings-item">
                        <label>Nombre de threads parallèles</label>
                        <input type="number" id="parallel-threads" min="1" max="16" value="4">
                    </div>
                    <div class="settings-item">
                        <label>Chargement asynchrone</label>
                        <input type="checkbox" id="async-loading" checked>
                    </div>
                </div>
                <div class="settings-group">
                    <h3>Statistiques</h3>
                    <div class="settings-item stats-display">
                        <div>Mémoire utilisée: <span id="memory-usage">0 MB</span></div>
                        <div>Temps de réponse moyen: <span id="avg-response">0 ms</span></div>
                        <div>Tables chargées: <span id="loaded-tables">0</span></div>
                        <div>Dernière analyse: <span id="last-analysis">-</span></div>
                    </div>
                    <button class="settings-btn" onclick="settingsManager.clearCache()">Vider le cache</button>
                </div>
            </div>
            <div id="settings-about" class="settings-pane">
                <h2>À propos</h2>
                <div class="about-logo">
                    <div class="app-logo-large">📊</div>
                    <div class="app-name-large">Lista State</div>
                    <div class="app-version">Version 1.0.0</div>
                </div>
                <div class="about-section">
                    <h3>Lista State - DSL Data Science</h3>
                    <p>Un langage dédié pour l'analyse de données, la manipulation de tables et les statistiques.</p>
                </div>
                <div class="about-section">
                    <h3>Fonctionnalités</h3>
                    <ul class="feature-list">
                        <li>✅ Chargement de données (CSV, Excel)</li>
                        <li>✅ Transformation de tables (SELECT, DROP, FILTER)</li>
                        <li>✅ Création de features (CREATE_FEATURE)</li>
                        <li>✅ Analyse statistique (AVG, SUM, COUNT, etc.)</li>
                        <li>✅ Agrégations et GROUP BY</li>
                        <li>✅ Visualisation des résultats</li>
                    </ul>
                </div>
                <div class="about-section">
                    <h3>Raccourcis clavier</h3>
                    <table class="shortcuts-table">
                        <tr><td><kbd>Ctrl</kbd> + <kbd>S</kbd></td><td>Sauvegarder</td></tr>
                        <tr><td><kbd>Ctrl</kbd> + <kbd>T</kbd></td><td>Sauvegarder la table courante</td></tr>
                        <tr><td><kbd>Ctrl</kbd> + <kbd>D</kbd></td><td>Supprimer l'analyse courante</td></tr>
                        <tr><td><kbd>Ctrl</kbd> + <kbd>Enter</kbd></td><td>Exécuter l'analyse</td></tr>
                        <tr><td><kbd>Esc</kbd></td><td>Fermer la modale</td></tr>
                    </table>
                </div>
                <div class="about-section">
                    <h3>Licence</h3>
                    <p>MIT License - 2024</p>
                </div>
            </div>
        </div>
    </div>
    <div class="settings-actions">
        <button class="settings-btn primary" onclick="settingsManager.saveSettings()">Sauvegarder</button>
        <button class="settings-btn" onclick="settingsManager.resetSettings()">Réinitialiser</button>
        <button class="settings-btn" onclick="settingsManager.exportSettings()">Exporter</button>
        <button class="settings-btn" onclick="settingsManager.importSettings()">Importer</button>
    </div>
</div>
    </div>
</div>
<div id="modal_table_utils" class="modal_table_utils">
    <div class="modal-content">
        <div class="title"></div>
        <div class="names_variables">
            <div class="grid-table-columns-variables" id="grid-table-columns-variables"></div>
        </div>
        <div class="func_utils" id="func_utils">
            <div class="save_changes_table" id="save_changes_table" onclick="dataManager.SaveChanges()">Save changes</div>
            <div class="add_row" id="add_row" onclick="dataManager.OpenModalAddRow()">Add row</div>
            <div class="add_column" id="add_column" onclick="dataManager.OpenModalAddColumn()">Add column</div>
            <div class="delete_column" id="delete_column" onclick="dataManager.OpenModalDeleteColumn()">Delete column</div>
            <div class="cancel">cancel</div>
        </div>
    </div>
</div>
<div id="modal_add_row" class="modal_add_row">
    <div class="modal-content">
        <div class="title">Add row to Table</div>
        <div class="div_editable"></div>
        <div class="submit_add_row" id="submit_add_row">Add that row</div>
        <div class="footer">
            <div class="cancel_add_row">Cancel</div>
        </div>
    </div>
</div>
<div id="modal_add_column" class="modal_add_column">
    <div class="modal_content">
        <div class="title">Add column</div>
        <div class="form">
            <label>Name of new column:</label>
            <input type="text" id="name_column_new" class="name_column_new">
        </div>
        <div class="add_column_new">Add column</div>
        <div class="cancel">Cancel</div>
    </div>
</div>
<div id="modal_delete_column" class="modal_delete_column">
    <div class="modal_content">
        <div class="title">Delete column</div>
        <div class="form">
            <label>Name of  column to delete:</label>
            <input type="text" id="name_column_delete" class="name_column_delete">
        </div>
        <div class="delete_column">Delete column</div>
        <div class="cancel">Cancel</div>
    </div>
</div>
<div id="modal-add-table" class="modal-add-table">
    <div class="modal-content">
        <div class="title">Add table</div>
        <div class="options">
            <div class="table_added active" onclick="dataManager.switchTabOption('new_table_option')">New table</div>
            <div class="table_added" onclick="dataManager.switchTabOption('old_table_option')">Import table</div>
        </div>
        <div class="main">
            <div id="new_table_option" class="table_option active">
                <div class="form-group-new-table">
                    <label>Table name:</label>
                    <input type="text" id="table_name_new" class="table_name_new">
                </div>
                <div class="form-group-new-table">
                    <label>Columns (separated by commas):</label>
                    <input type="text" id="table_columns_new" class="table_columns_new">
                </div>
                <div class="create_new_table" onclick="dataManager.CreateNewTable()">Create table</div>
            </div>
            <div id="old_table_option" class="table_option">
                <div class="import_table" onclick="dataManager.ImportTable()">Import table</div>
            </div>
        </div>
        <div class="footer">
            <div class="cancel" id="cancel">Cancel</div>
        </div>
    </div>
</div>
<div id="modal-delete-table" class="modal-delete-table">
    <div class="modal-content">
        <div class="title">Delete table</div>
        <div class="form-group-delete-table">
            <label>Name of table to delete:</label>
            <input type="text" id="name_table_to_delete">
        </div>
        <div class="delete-table-aply" onclick="dataManager.DeleteTable()">Delete Table</div>
        <div class="cancel">Cancel</div>
    </div>
</div>
<div id="modal-new-analysis" class="modal-new-analysis">
    <div class="modal-content">
        <div class="title">New file of analysis</div>
        <div class="input">
            <input type="text" id="name_file_analysis">
        </div>
        <div class="btns">
            <div class="add_new">Add new</div>
            <div class="cancel">cancel</div>
        </div>
    </div>
</div>
<div id="modal-delete-analysis" class="modal-delete-analysis">
    <div class="modal-content">
        <div class="title">Delete a file of analysis</div>
        <div class="input">
            <input type="text" id="name_file_delete">
        </div>
        <div class="btns">
            <div class="delete">Delete one</div>
            <div class="cancel">cancel</div>
        </div>
    </div>
</div>
 <script>
 
const DataCore = {
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

    getSettings() {
        return this.core.payload.settings;
    }


   async saveSettings() {
        this.saveSettingsFromUI();
        await this.core.save();
        this.applySettings();
        this.showNotification('Paramètres sauvegardés', 'success');
    }


    loadSettingsToUI() {
        const settings = this.getSettings();

        document.getElementById('default-session').value = settings.general?.defaultSession || 'new';
        document.getElementById('auto-save').checked = settings.general?.autoSave ?? true;
        document.getElementById('auto-save-interval').value = settings.general?.autoSaveInterval || 30;
        document.getElementById('default-folder').value = settings.general?.defaultFolder || '';
        document.getElementById('default-export-format').value = settings.general?.defaultExportFormat || 'csv';


        document.getElementById('editor-theme').value = settings.editor?.theme || 'dracula';
        document.getElementById('editor-font-size').value = settings.editor?.fontSize || 14;
        document.getElementById('editor-font-family').value = settings.editor?.fontFamily || "'Fira Code', monospace";
        document.getElementById('editor-ligatures').checked = settings.editor?.ligatures ?? true;
        document.getElementById('editor-indentation').value = settings.editor?.indentation || 'spaces-4';
        document.getElementById('editor-autocomplete').checked = settings.editor?.autocomplete ?? true;
        document.getElementById('editor-highlight-line').checked = settings.editor?.highlightLine ?? true;
        document.getElementById('editor-line-numbers').checked = settings.editor?.lineNumbers ?? true;


        document.getElementById('app-theme').value = settings.appearance?.theme || 'dark';
        document.getElementById('accent-color').value = settings.appearance?.accentColor || '#4299e1';
        document.getElementById('ui-density').value = settings.appearance?.density || 'comfortable';
        document.getElementById('show-previews').checked = settings.appearance?.showPreviews ?? true;
        document.getElementById('sidebar-collapsed').checked = settings.appearance?.sidebarCollapsed || false;


        document.getElementById('memory-limit').value = settings.performance?.memoryLimit || 2048;
        document.getElementById('data-cache').checked = settings.performance?.dataCache ?? true;
        document.getElementById('cache-size').value = settings.performance?.cacheSize || 512;
        document.getElementById('parallel-threads').value = settings.performance?.parallelThreads || 4;
        document.getElementById('async-loading').checked = settings.performance?.asyncLoading ?? true;
    }


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

    applySettings() {
        this.applyTheme();
        this.applyEditorSettings();
        this.applyAppearanceSettings();

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


applyAppearanceSettings() {
    const settings = this.getSettings();
    const density = settings.appearance?.density || 'comfortable';
    const container = document.querySelector('.app-shell');
    const sideLeft = document.querySelector('.side-left');

    if (!sideLeft) return;

    container.classList.remove('density-compact', 'density-spacious');
    if (density !== 'comfortable') {
        container.classList.add(`density-${density}`);
    }


    if (settings.appearance?.sidebarCollapsed) {

        sideLeft.style.transition = 'width 0.3s ease, padding 0.3s ease';
        sideLeft.style.width = '80px';
        sideLeft.style.padding = '30px 5px';

        sideLeft.querySelectorAll('.nav-item').forEach(item => {
            const icon = item.querySelector('.menu-icon');
            const originalText = item.textContent.trim().replace('✓', '').trim();

            item.setAttribute('data-original-text', originalText);

            if (icon) {
                item.innerHTML = '';
                item.appendChild(icon);
            }

            item.setAttribute('title', originalText);

            item.style.justifyContent = 'center';
            item.style.padding = '15px 0';
            item.style.margin = '5px 0';
            item.style.borderRadius = '8px';

            if (icon) {
                icon.style.fontSize = '24px';
                icon.style.margin = '0';
            }
        });

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

        const spacer = sideLeft.querySelector('.spacer');
        if (spacer) {
            spacer.style.display = 'none';
        }

        document.querySelectorAll('.session-tile-data').forEach(el => {
            el.setAttribute('data-full-text', el.textContent);
            el.style.fontSize = '12px';
            el.style.justifyContent = 'center';
        });

    } else {
        sideLeft.style.transition = 'width 0.3s ease, padding 0.3s ease';
        sideLeft.style.width = '280px';
        sideLeft.style.padding = '30px 20px';

        const navTexts = ['Data Editor', 'Data Analysis', 'Session', 'Settings'];

        sideLeft.querySelectorAll('.nav-item').forEach((item, index) => {
            const icon = item.querySelector('.menu-icon');
            const originalText = item.getAttribute('data-original-text') || navTexts[index] || '';

            if (icon) {
                item.innerHTML = '';
                item.appendChild(icon);
                item.appendChild(document.createTextNode(` ${originalText}`));

                icon.style.fontSize = '20px';
                icon.style.margin = '';
            }

            item.removeAttribute('title');

            item.style.justifyContent = 'space-between';
            item.style.padding = '15px 20px';
            item.style.margin = '0';
            item.style.borderRadius = '12px';
        });

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

        const spacer = sideLeft.querySelector('.spacer');
        if (spacer) {
            spacer.style.display = 'block';
        }

        document.querySelectorAll('.session-tile-data').forEach(el => {
            const fullText = el.getAttribute('data-full-text') || 'New session';
            el.textContent = fullText;
            el.style.fontSize = '16px';
            el.style.justifyContent = '';
        });
    }
}


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


    async clearCache() {
        if (confirm('Vider le cache ?')) {
            // Implémentation spécifique à votre application
            this.showNotification('Cache vidé', 'success');
        }
    }

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

        const autoSaveInputs = document.querySelectorAll('#settings input, #settings select');
        autoSaveInputs.forEach(input => {
            input.addEventListener('change', () => {
                const settings = this.getSettings();
                if (settings.general?.autoSave) {
                    this.saveSettings();
                }
            });
        });


        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's' && document.getElementById('settings').classList.contains('active')) {
                e.preventDefault();
                this.saveSettings();
            }
        });
    }
}


const settingsManager = new SettingsManager();


// Constante pour marquer les valeurs manquantes
const MISSING_VALUE = null;  // Utiliser null pour les valeurs manquantes
const EMPTY_STRING = "";      // Chaîne vide intentionnelle

class DataTableManager {
    constructor() {
        this.core = DataCore;
        this.currentNameTable = null;
        this.grid_table = document.querySelector(".data-table .grid-table");
        this.list_table = document.querySelector(".data-table .list-table");
    }

    async init() {
        window.addEventListener("pywebviewready", async () => {
            const initial = await pywebview.api.initial_data();

            if (initial && initial.error) {
                alert(`Erreur: ${initial.error}`);
                return;
            }
            if (initial && initial.success) {
                this.core.update(initial.name, initial.data);
                this.refreshUI();

                settingsManager.init();

                const session_tile = document.querySelectorAll(".session-tile-data");
                session_tile.forEach(tile => {
                    tile.innerHTML = `<div>Session - ${this.core.sessionName}</div>`;
                });
            }
        });
    }

    refreshUI() {
        const firstTable = Object.keys(this.core.payload.tables)[0];
        if (firstTable) {
            this.displayTable(firstTable);
            this.currentNameTable = firstTable;
        }
        this.displayListTable();
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

    // Helper pour afficher les valeurs de manière appropriée
    formatCellValue(value) {
        if (value === null) {
            return "⚪";  // Symbole pour valeur manquante
        }
        if (value === "") {
            return "␣";  // Symbole pour chaîne vide (optionnel)
        }
        return String(value);
    }

    // Helper pour parser les valeurs depuis l'affichage
    parseCellValue(textContent) {
        if (textContent === "⚪") {
            return null;  // Valeur manquante
        }
        if (textContent === "␣") {
            return null;    // Chaîne vide intentionnelle
        }
        return textContent;  // Valeur normale
    }

    displayTable(name) {
        const tableData = this.core.payload.tables[name];
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
                const value = rows[r][c];

                // Formatage spécial pour null et chaîne vide
                cell.textContent = this.formatCellValue(value);

                // Styling optionnel pour distinguer
                if (value === null) {
                    cell.style.color = "#999";
                    cell.style.fontStyle = "italic";
                } else if (value === "") {
                    cell.style.color = "#ccc";
                }

                cell.contentEditable = true;
                row.appendChild(cell);
            }
            table.appendChild(row);
        }

        this.grid_table.appendChild(table);
    }

    displayListTable() {
        this.list_table.innerHTML = '';
        for (let name of Object.keys(this.core.payload.tables)) {
            let list = document.createElement("div");
            list.className = "list-table-item";
            list.innerHTML = `<div ondblclick="dataManager.OpenModalTableUtils(this)" onclick="dataManager.playTable(this)">${name}</div>`;
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
        const nameInput = document.getElementById("name-session");
        if (!nameInput || !nameInput.value) {
            alert("Veuillez entrer un nom de session");
            return;
        }

        try {
            const result = await pywebview.api.ChoosePathNewSession(nameInput.value);

            if (result && result.error) {
                alert(`Erreur: ${result.error}`);
                return;
            }
            if (result && result.cancelled) {
                return;
            }

            if (result && result.success) {
                await this.handleNewSession(result.name, result.data);
            }

        } catch (error) {
            console.error("Erreur:", error);
            alert("Une erreur est survenue lors de la création de la session");
        }
    }

    async handleNewSession(name, data) {
        this.core.sessionName = name;
        this.core.payload = data;

        const session_tiles = document.querySelectorAll(".session-tile-data");
        session_tiles.forEach(tile => {
            tile.innerHTML = `<div>Session - ${name}</div>`;
        });

        const first_table = Object.keys(data.tables)[0];
        if (first_table) {
            this.currentNameTable = first_table;
            this.displayTable(first_table);
        }
        this.displayListTable();

        if (window.analysisManager) {
            window.analysisManager.displayListAnalysis();
            const firstAnalysis = Object.keys(data.analysis)[0];
            if (firstAnalysis) {
                window.analysisManager.currentAnalysisName = firstAnalysis;
                window.analysisManager.displayAnalysis(firstAnalysis);
            } else {
                window.analysisManager.editor.value = "";
                window.analysisManager.updateLineNumbers();
            }
        }

        await this.core.save();

        alert(`Session "${name}" créée avec succès !`);
    }

    async ChoosePathSessionLife() {
        try {
            const name_session = await pywebview.api.open_file_dialog();

            if (name_session && name_session.error) {
                alert(`Erreur: ${name_session.error}`);
                return;
            }

            if (name_session && name_session.success) {
                this.core.sessionName = name_session.name;
                this.core.payload = name_session.data;

                settingsManager.init();

                const session_tile = document.querySelectorAll(".session-tile-data");
                session_tile.forEach(tile => {
                    tile.innerHTML = `<div>Session - ${this.core.sessionName}</div>`;
                });

                const first_table = Object.keys(this.core.payload.tables)[0];
                if (first_table) {
                    this.currentNameTable = first_table;
                    this.displayTable(first_table);
                } else {
                    this.grid_table.innerHTML = '<div class="empty-state">Aucune table dans cette session</div>';
                }
                this.displayListTable();

                if (window.analysisManager) {
                    window.analysisManager.displayListAnalysis();
                    const firstAnalysis = Object.keys(this.core.payload.analysis)[0];
                    if (firstAnalysis) {
                        window.analysisManager.currentAnalysisName = firstAnalysis;
                        window.analysisManager.displayAnalysis(firstAnalysis);
                    } else {
                        window.analysisManager.editor.value = "";
                        window.analysisManager.updateLineNumbers();
                    }
                }
            }
        } catch (error) {
            alert("Une erreur est survenue lors du chargement de la session.");
        }
    }

    playTable(me) {
        this.SaveCurrentTable();
        this.currentNameTable = me.innerText;
        this.displayTable(me.innerText);
    }

    OpenModalTableUtils(me) {
        this.SaveCurrentTable();
        this.displayTable(me?.innerText);
        const modal = document.getElementById("modal_table_utils");
        modal.style.display = "flex";

        const title_modal = document.querySelector(".modal_table_utils .modal-content .title");
        const name_ = me?.innerText || "Table inconnue";
        title_modal.innerHTML = `<h2>Table: ${name_}</h2>`;

        this.currentNameTable = name_ !== "Table inconnue" ? name_ : this.currentNameTable;

        if (name_ === "Table inconnue") {
            modal.style.display = "none";
            return;
        }

        const table = document.getElementById("grid-table-columns-variables");
        table.innerHTML = "";

        const columns = Object.keys(this.core.payload.tables[this.currentNameTable])
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
            div_var.textContent = i === 0 ? "Name's variable" : columns[i - 1];
            div_var.contentEditable = i === 0 ? "false" : "true";
            table.appendChild(div_var);
        }

        table.style.display = "grid";
        table.style.gridTemplateColumns = `repeat(${nbColumns + 1}, 300px)`;
    }

    OpenModalAddRow() {
        if (!this.currentNameTable || !this.core.payload.tables[this.currentNameTable]) {
            alert("Aucune table sélectionnée !");
            return;
        }

        document.querySelector(".modal_add_row").style.display = "flex";
        const div_editable = document.querySelector(".modal_add_row .modal-content .div_editable");

        div_editable.innerHTML = "";

        const columns = Object.keys(this.core.payload.tables[this.currentNameTable]);
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
            cell.textContent = "";  // Vide par défaut = chaîne vide intentionnelle
            div_editable.appendChild(cell);
        }
    }

    setupEventListeners() {
        document.getElementById("submit_add_row").addEventListener("click", async (e) => {
            e.stopPropagation();

            if (!this.currentNameTable || !this.core.payload.tables[this.currentNameTable]) {
                alert("Aucune table sélectionnée !");
                return;
            }

            const tableData = this.core.payload.tables[this.currentNameTable];

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

            // Permettre les cellules vides (qui seront des chaînes vides intentionnelles)
            // Note: on ne force plus à remplir toutes les cellules

            const newRowData = {};

            for (let i = 0; i < columns_for_added.length; i++) {
                // Si l'utilisateur a laissé vide, c'est une chaîne vide intentionnelle
                newRowData[columns_for_added[i]] = datas_added_for_row[i] === "" ? EMPTY_STRING : datas_added_for_row[i];
            }

            const columns = Object.keys(tableData);

            for (let column of columns) {
                if (!Array.isArray(tableData[column])) {
                    console.error(`Erreur: ${column} n'est pas un tableau`);
                    continue;
                }
                // Si la colonne n'est pas dans newRowData, c'est une valeur manquante (null)
                const valueToAdd = newRowData[column] !== undefined ? newRowData[column] : MISSING_VALUE;
                tableData[column].push(valueToAdd);
            }

            const rowCounts = columns.map(col => tableData[col].length);
            const allSameLength = rowCounts.every(count => count === rowCounts[0]);

            if (!allSameLength) {
                const targetLength = Math.max(...rowCounts);
                for (let column of columns) {
                    while (tableData[column].length < targetLength) {
                        tableData[column].push(MISSING_VALUE);  // Valeur manquante pour les trous
                    }
                }
            }

            this.displayTable(this.currentNameTable);
            await this.core.save();

            document.getElementById("modal_add_row").style.display = "none";

            const div_editable = document.querySelector(".modal_add_row .modal-content .div_editable");
            const valueCells = div_editable.querySelectorAll(".add_row.value");
            valueCells.forEach(cell => cell.textContent = "");
        });

        document.querySelector(".modal_add_row .modal-content .footer .cancel_add_row").addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById("modal_add_row").style.display = "none";
        });

        document.querySelector("#modal_add_column .add_column_new").addEventListener("click", async (e) => {
            e.stopPropagation();

            const input = document.getElementById("name_column_new");
            const new_column_added = input.value.trim();

            const Columns = Object.keys(this.core.payload.tables[this.currentNameTable])
            const currentTable = this.core.payload.tables[this.currentNameTable];

            if (new_column_added && this.currentNameTable !== "") {
                if (Columns.includes(new_column_added)) {
                    alert("Cette colonne existe déjà !");
                    return;
                }

                const rowCount = Columns.length > 0 ? currentTable[Columns[0]].length : 0;
                // Nouvelle colonne initialisée avec des valeurs manquantes (null)
                currentTable[new_column_added] = Array(rowCount).fill(MISSING_VALUE);

                this.displayTable(this.currentNameTable);
                await this.core.save();
                input.value = "";
                document.getElementById("modal_add_column").style.display = "none";
                document.getElementById("modal_table_utils").style.display = "none";
            }
        });

        document.querySelector("#modal_delete_column .delete_column").addEventListener("click", async (e) => {
            e.stopPropagation();

            const input = document.getElementById("name_column_delete");
            const new_column_delete = input.value.trim();

            const Columns = Object.keys(this.core.payload.tables[this.currentNameTable])

            if (new_column_delete && this.currentNameTable !== NaN) {
                if (!Columns.includes(new_column_delete)) {
                    alert("Cette colonne n'existe pas !");
                    return;
                }

                delete this.core.payload.tables[this.currentNameTable][new_column_delete];

                this.displayTable(this.currentNameTable);
                await this.core.save();
                input.value = "";
                document.getElementById("modal_delete_column").style.display = "none";
                document.getElementById("modal_table_utils").style.display = "none";
            }
        });

        document.querySelector(".modal-add-table .modal-content .footer .cancel").addEventListener("click", function (e) {
            e.preventDefault();
            document.getElementById("modal-add-table").style.display = "none";
        });

        document.querySelector(".modal-delete-table .modal-content .cancel").addEventListener("click", function () {
            document.getElementById("modal-delete-table").style.display = "none";
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

        document.querySelector(".modal_add_column .modal_content .cancel").addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById("modal_add_column").style.display = "none";
        });

        document.querySelector(".modal_delete_column .modal_content .cancel").addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById("modal_delete_column").style.display = "none";
        });

        document.querySelector(".modal_table_utils .modal-content .func_utils .cancel").addEventListener("click", (e) => {
            e.stopPropagation();
            document.getElementById("modal_table_utils").style.display = "none";
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

        document.addEventListener("keydown", (e) => {
            if (e.ctrlKey && (e.key === 't' || e.key === 'T')) {
                e.preventDefault();
                this.SaveCurrentTable();
            }
        });

        document.addEventListener("keydown", async (e) => {
            if (e.ctrlKey && (e.key === "s" || e.key === "S")) {
                e.preventDefault();
                await pywebview.api.save_as(this.datas)
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
        if (!this.currentNameTable || !this.core.payload.tables[this.currentNameTable]) {
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
                const cellText = editableCells[cellIndex]?.textContent;

                // Utiliser parseCellValue pour interpréter l'affichage
                const cellValue = this.parseCellValue(cellText);
                changedDatas[columnsNames[colIndex]].push(cellValue);
            }
        }

        this.core.payload.tables[this.currentNameTable] = changedDatas;
        this.displayTable(this.currentNameTable);

        pywebview.api.save_as(this.datas);
        document.getElementById("modal_table_utils").style.display = "none";
        console.log("Changements sauvegardés avec succès !", changedDatas);
    }

    async SaveCurrentTable() {
        if (!this.currentNameTable) {
            alert("Aucune table sélectionnée !");
            return;
        }

        const changedDatas = {};
        const divValues = document.querySelectorAll(".data-table .grid-table table th");
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
                const cellText = editableCells[cellIndex]?.textContent;
                
                // Utiliser parseCellValue pour interpréter l'affichage
                const cellValue = this.parseCellValue(cellText);
                changedDatas[columnsNames[colIndex]].push(cellValue);
            }
        }

        this.core.payload.tables[this.currentNameTable] = changedDatas;
        await this.core.save();
    }

    switchTabOption(id) {
        document.querySelectorAll(".table_added").forEach(tab => {
            tab.classList.remove("active");
        });
        document.querySelectorAll(".table_option").forEach(tab => {
            tab.classList.remove("active");
        });
        document.getElementById(id).classList.add("active");
        event.currentTarget.classList.add("active");
    }

    openModalAddTable() {
        document.getElementById("modal-add-table").style.display = "flex";
    }

    openModalDeleteTable() {
        document.getElementById("modal-delete-table").style.display = "flex";
    }

    async CreateNewTable() {
        if (!this.core.sessionName) {
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

        if (this.core.payload.tables[tableName]) {
            alert(`La table "${tableName}" existe déjà !`);
            return;
        }

        const tableDatas = {};
        const initialRows = 3;
        for (let name_column of names_columns) {
            // Initialiser avec des valeurs manquantes (null) plutôt que chaînes vides
            tableDatas[name_column] = Array(initialRows).fill(MISSING_VALUE);
        }

        this.core.payload.tables[tableName] = tableDatas;

        await this.core.save();

        this.currentNameTable = tableName;
        this.displayTable(tableName);
        this.displayListTable();

        nameInput.value = "";
        columnsInput.value = "";

        document.getElementById("modal-add-table").style.display = "none";
    }

    async DeleteTable() {
        if (!this.core.sessionName) {
            alert("Aucune session sélectionnée !");
            return;
        }

        const tableNameInput = document.getElementById("name_table_to_delete");
        const tableName = tableNameInput?.value.trim();

        if (!tableName) {
            alert("Veuillez entrer un nom de table !");
            return;
        }

        if (!this.core.payload.tables || !this.core.payload.tables[tableName]) {
            alert(`La table "${tableName}" n'existe pas !`);
            return;
        }

        const confirmDelete = confirm(`Êtes-vous sûr de vouloir supprimer la table "${tableName}" ?\nCette action est irréversible !`);

        if (!confirmDelete) {
            return;
        }

        try {
            delete this.core.payload.tables[tableName];
            await this.core.save();

            this.displayListTable();

            const remainingTables = Object.keys(this.core.payload.tables);
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

            alert(`Table "${tableName}" supprimée avec succès !`);

        } catch (error) {
            alert("Une erreur est survenue lors de la suppression de la table.");
        }
    }

    async ImportTable() {
        const imports_table = await pywebview.api.import_table();

        if (imports_table && imports_table.length === 2) {
            this.core.payload.tables[imports_table[0]] = imports_table[1];

            await this.core.save();
            const name_table = imports_table[0];
            this.currentNameTable = name_table;
            this.displayTable(name_table);
            this.displayListTable();

            if (window.analysisManager) {
                window.analysisManager.displayListAnalysis();
                const firstAnalysis = Object.keys(this.core.payload.analysis)[0];
                if (firstAnalysis) window.analysisManager.displayAnalysis(firstAnalysis);
            }

            document.getElementById("modal-add-table").style.display = "none";
        } else {
            alert("Erreur d'import de la table.");
        }
    }
}

const dataManager = new DataTableManager();
dataManager.init();
dataManager.setupEventListeners();

window.dataManager = dataManager
window.settingsManager = settingsManager;


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

           const first_analysis = Object.keys(this.core.payload.analysis)[0];
           if (first_analysis){
                this.displayAnalysis(first_analysis);
                this.currentAnalysisName = first_analysis;
                this.displayListAnalysis();
           }
        }, 300);
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
                alert(`L'analyse ${name_analysis_new} existe déjà.`);
                return;
             }

            this.core.payload.analysis[name_analysis_new] = "# Nouvelle analyse\nLoad demo as data\nDescribe demo";
            this.currentAnalysisName = name_analysis_new;
            this.displayAnalysis(this.currentAnalysisName);
            this.displayListAnalysis();
            await this.core.save();
            document.getElementById("modal-new-analysis").style.display="none";
            alert(`Le fichier d'analyse ${name_analysis_new} est sauvegardé avec succès.`);
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

        document.querySelector(".analysis .left .bottom .box .run").addEventListener("click", async (e) => {
            e.preventDefault();
            await this.runAnalysis();
        });

        // Ajouter un écouteur pour la touche Echap en plein écran
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.fullscreenElement) {
                document.exitFullscreen();
            }
        });
    }

    async deleteAnalysis(name){
        if(!this.core.sessionName){
            alert("Aucune session selectionnée!");
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
        alert(`L'analyse ${name} supprimée avec succès!`);
    }

    async saveCurrentAnalysis(){
        if(!this.currentAnalysisName){
            alert(`Aucune analyse selectionnée!`);
            return;
        }

        const content_analysis = this.editor.value;
        this.core.payload.analysis[this.currentAnalysisName] = content_analysis;
        await this.core.save();
    }

    async runAnalysis() {
        const code = this.editor.value;
        const settings = this.core.getSettings();

        await this.saveCurrentAnalysis();

        const result = await pywebview.api.evaluate_dsl(code, this.core.payload);

        if (result.success) {
            this.core.payload = result.datas;
            displayEvaluatorResults(result.messages, settings);
            await this.core.save();
        } else {
            displayEvaluatorResults(result.messages || [{
                type: 'error',
                content: result.errors?.join('\n') || 'Erreur inconnue'
            }], settings);
        }
    }
}

// ========== FONCTIONS D'AFFICHAGE DES RÉSULTATS ==========

function displayEvaluatorResults(results, settings = {}) {
    const rightPanel = document.querySelector(".analysis .right");
    if (!rightPanel) return;

    rightPanel.innerHTML = "";

    if (!results || results.length === 0) {
        rightPanel.innerHTML = '<div class="no-results">Aucun résultat à afficher</div>';
        return;
    }

    const resultsContainer = document.createElement("div");
    resultsContainer.className = "evaluator-results";

    // Grouper les résultats par type
    const groupedResults = {
        table: [],
        analysis: [],
        stats: [],
        describe: [],
        describe_all: [],
        summary: [],
        svg: [],
        info: [],
        success: [],
        error: []
    };

    results.forEach(result => {
        if (result.type === 'svg') {
            groupedResults.svg.push(result);
        } else if (result.type === 'analysis' && result.content?.type === 'stats') {
            groupedResults.stats.push(result);
        } else if (result.type === 'analysis' && result.content?.type === 'describe') {
            groupedResults.describe.push(result.content);
        } else if (result.type === 'analysis' && result.content?.type === 'describe_all') {
            groupedResults.describe_all.push(result.content);
        } else if (result.type === 'analysis' && result.content?.type === 'summary') {
            groupedResults.summary.push(result.content);
        } else if (groupedResults[result.type]) {
            groupedResults[result.type].push(result);
        } else {
            groupedResults.info.push(result);
        }
    });

    // Afficher les erreurs en premier
    if (groupedResults.error.length > 0) {
        const errorSection = createErrorSection(groupedResults.error);
        resultsContainer.appendChild(errorSection);
    }

    // Afficher les graphiques SVG
    if (groupedResults.svg.length > 0) {
        const svgSection = createSVGSection(groupedResults.svg);
        resultsContainer.appendChild(svgSection);
    }

    // Afficher les tables
    if (groupedResults.table.length > 0) {
        const tableSection = createTableSection(groupedResults.table);
        resultsContainer.appendChild(tableSection);
    }

    // Afficher les résumés
    if (groupedResults.summary.length > 0) {
        groupedResults.summary.forEach(summary => {
            const summarySection = createSummarySection(summary);
            resultsContainer.appendChild(summarySection);
        });
    }

    // Afficher les statistiques descriptives
    if (groupedResults.describe.length > 0) {
        groupedResults.describe.forEach(describe => {
            const describeSection = createDescribeSection(describe);
            resultsContainer.appendChild(describeSection);
        });
    }

    // Afficher les statistiques complètes
    if (groupedResults.describe_all.length > 0) {
        groupedResults.describe_all.forEach(describeAll => {
            const describeAllSection = createDescribeAllSection(describeAll);
            resultsContainer.appendChild(describeAllSection);
        });
    }

    // Afficher les analyses standards
    if (groupedResults.analysis.length > 0) {
        const analysisSection = createAnalysisSection(groupedResults.analysis);
        resultsContainer.appendChild(analysisSection);
    }

    // Afficher les statistiques avancées
    if (groupedResults.stats.length > 0) {
        const statsSection = createStatsSection(groupedResults.stats);
        resultsContainer.appendChild(statsSection);
    }

    // Afficher les informations et succès
    if (groupedResults.success.length > 0 || groupedResults.info.length > 0) {
        const infoSection = createInfoSection([...groupedResults.success, ...groupedResults.info]);
        resultsContainer.appendChild(infoSection);
    }

    rightPanel.appendChild(resultsContainer);
}

// ========== SECTION POUR LES STATISTIQUES DESCRIPTIVES ==========

function createDescribeSection(results) {
    const section = document.createElement("div");
    section.className = "results-section describe-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📊 Statistiques descriptives - ${results.target || 'Table'}`;
    section.appendChild(title);

    const results_data = results.results || {};
    const format = results.format || 'table';

    if (Object.keys(results_data).length === 0) {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne numérique trouvée";
        section.appendChild(emptyMsg);
        return section;
    }

    if (format === 'table') {
        // Format tableau
        const tableWrapper = document.createElement("div");
        tableWrapper.className = "table-wrapper stats-table";

        const table = document.createElement("table");
        table.className = "stats-table";

        // En-tête
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        
        const thMetric = document.createElement("th");
        thMetric.textContent = "Métrique";
        headerRow.appendChild(thMetric);
        
        Object.keys(results_data).forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Corps
        const tbody = document.createElement("tbody");
        
        // Liste des métriques
        const metrics = [
            { key: 'count', label: 'Count' },
            { key: 'mean', label: 'Mean' },
            { key: 'std', label: 'Std Dev' },
            { key: 'min', label: 'Min' },
            { key: '25%', label: '25%' },
            { key: '50%', label: '50% (Median)' },
            { key: '75%', label: '75%' },
            { key: 'max', label: 'Max' },
            { key: 'skew', label: 'Skewness' },
            { key: 'kurt', label: 'Kurtosis' }
        ];

        metrics.forEach(metric => {
            const row = document.createElement("tr");
            
            const tdMetric = document.createElement("td");
            tdMetric.className = "metric-name";
            tdMetric.textContent = metric.label;
            row.appendChild(tdMetric);
            
            Object.keys(results_data).forEach(col => {
                const td = document.createElement("td");
                const value = results_data[col]?.[metric.key];
                
                if (value === undefined || value === null || isNaN(value)) {
                    td.textContent = "-";
                    td.className = "null-value";
                } else if (typeof value === 'number') {
                    td.textContent = value.toFixed(4);
                    td.className = "number-value";
                } else {
                    td.textContent = value;
                }
                
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        tableWrapper.appendChild(table);
        section.appendChild(tableWrapper);

    } else {
        // Format cartes
        const cardsGrid = document.createElement("div");
        cardsGrid.className = "stats-cards-grid";

        Object.entries(results_data).forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Mean', value: stats.mean },
                { label: 'Std Dev', value: stats.std },
                { label: 'Min', value: stats.min },
                { label: '25%', value: stats['25%'] },
                { label: 'Median', value: stats['50%'] },
                { label: '75%', value: stats['75%'] },
                { label: 'Max', value: stats.max },
                { label: 'Skewness', value: stats.skew },
                { label: 'Kurtosis', value: stats.kurt }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null || isNaN(stat.value)) {
                    statValue.textContent = "-";
                    statValue.classList.add("null-value");
                } else if (typeof stat.value === 'number') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            cardsGrid.appendChild(card);
        });

        section.appendChild(cardsGrid);
    }

    return section;
}

// ========== SECTION POUR LES STATISTIQUES COMPLÈTES ==========

function createDescribeAllSection(results) {
    const section = document.createElement("div");
    section.className = "results-section describe-all-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📈 Statistiques complètes - ${results.target || 'Table'}`;
    section.appendChild(title);

    // Informations générales
    if (results.shape) {
        const infoBar = document.createElement("div");
        infoBar.className = "info-bar";
        infoBar.innerHTML = `
            <span class="info-badge">📊 ${results.shape[0]} lignes</span>
            <span class="info-badge">📋 ${results.shape[1]} colonnes</span>
        `;
        section.appendChild(infoBar);
    }

    const results_data = results.results || {};
    const format = results.format || 'detailed';

    const tabsContainer = document.createElement("div");
    tabsContainer.className = "stats-tabs";

    const numericTab = document.createElement("div");
    numericTab.className = "stats-tab active";
    numericTab.textContent = "Numériques";
    
    const categoricalTab = document.createElement("div");
    categoricalTab.className = "stats-tab";
    categoricalTab.textContent = "Catégorielles";

    tabsContainer.appendChild(numericTab);
    tabsContainer.appendChild(categoricalTab);
    section.appendChild(tabsContainer);

    // Conteneur pour les données numériques
    const numericContainer = document.createElement("div");
    numericContainer.className = "stats-content active";

    // Conteneur pour les données catégorielles
    const categoricalContainer = document.createElement("div");
    categoricalContainer.className = "stats-content";

    // Séparer les colonnes par type
    const numericCols = [];
    const categoricalCols = [];

    Object.entries(results_data).forEach(([colName, info]) => {
        if (info.type === 'numeric') {
            numericCols.push([colName, info]);
        } else {
            categoricalCols.push([colName, info]);
        }
    });

    // Afficher les colonnes numériques
    if (numericCols.length > 0) {
        const numericGrid = document.createElement("div");
        numericGrid.className = "stats-cards-grid";

        numericCols.forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card numeric";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3><span class="col-type">🔢 numérique</span>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Missing', value: stats.missing },
                { label: 'Mean', value: stats.mean },
                { label: 'Std Dev', value: stats.std },
                { label: 'Min', value: stats.min },
                { label: 'Max', value: stats.max },
                { label: 'Median', value: stats.median }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null || isNaN(stat.value)) {
                    statValue.textContent = "-";
                    statValue.classList.add("null-value");
                } else if (typeof stat.value === 'number') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            numericGrid.appendChild(card);
        });

        numericContainer.appendChild(numericGrid);
    } else {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne numérique";
        numericContainer.appendChild(emptyMsg);
    }

    // Afficher les colonnes catégorielles
    if (categoricalCols.length > 0) {
        const categoricalGrid = document.createElement("div");
        categoricalGrid.className = "stats-cards-grid";

        categoricalCols.forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card categorical";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3><span class="col-type">🏷️ catégorielle</span>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Missing', value: stats.missing },
                { label: 'Unique', value: stats.unique },
                { label: 'Top', value: stats.top },
                { label: 'Freq', value: stats.freq },
                { label: 'Entropy', value: stats.entropy }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null) {
                    statValue.textContent = "-";
                } else if (typeof stat.value === 'number' && stat.label === 'Entropy') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            categoricalGrid.appendChild(card);
        });

        categoricalContainer.appendChild(categoricalGrid);
    } else {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne catégorielle";
        categoricalContainer.appendChild(emptyMsg);
    }

    section.appendChild(numericContainer);
    section.appendChild(categoricalContainer);

    // Gestion des onglets
    numericTab.addEventListener('click', () => {
        numericTab.classList.add('active');
        categoricalTab.classList.remove('active');
        numericContainer.classList.add('active');
        categoricalContainer.classList.remove('active');
    });

    categoricalTab.addEventListener('click', () => {
        categoricalTab.classList.add('active');
        numericTab.classList.remove('active');
        categoricalContainer.classList.add('active');
        numericContainer.classList.remove('active');
    });

    return section;
}

// ========== SECTION POUR LE RÉSUMÉ ==========

function createSummarySection(results) {
    const section = document.createElement("div");
    section.className = "results-section summary-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📋 Résumé - ${results.target || 'Table'}`;
    section.appendChild(title);

    const results_data = results.results || {};

    const summaryGrid = document.createElement("div");
    summaryGrid.className = "summary-grid";

    const metrics = [
        { label: 'Lignes', value: results_data.shape?.[0] },
        { label: 'Colonnes', value: results_data.shape?.[1] },
        { label: 'Total cellules', value: results_data.total_cells },
        { label: 'Cellules manquantes', value: results_data.missing_cells },
        { label: 'Colonnes numériques', value: results_data.numeric_columns },
        { label: 'Colonnes catégorielles', value: results_data.categorical_columns }
    ];

    metrics.forEach(metric => {
        const card = document.createElement("div");
        card.className = "summary-card";

        const value = document.createElement("div");
        value.className = "summary-value";
        value.textContent = metric.value !== undefined ? metric.value : '-';

        const label = document.createElement("div");
        label.className = "summary-label";
        label.textContent = metric.label;

        card.appendChild(value);
        card.appendChild(label);
        summaryGrid.appendChild(card);
    });

    section.appendChild(summaryGrid);

    // Liste des colonnes
    if (results_data.columns && results_data.columns.length > 0) {
        const columnsList = document.createElement("div");
        columnsList.className = "columns-list";

        const columnsTitle = document.createElement("div");
        columnsTitle.className = "columns-title";
        columnsTitle.textContent = "Colonnes:";
        columnsList.appendChild(columnsTitle);

        const columnsGrid = document.createElement("div");
        columnsGrid.className = "columns-grid";

        results_data.columns.forEach(col => {
            const colTag = document.createElement("span");
            colTag.className = "column-tag";
            colTag.textContent = col;
            columnsGrid.appendChild(colTag);
        });

        columnsList.appendChild(columnsGrid);
        section.appendChild(columnsList);
    }

    return section;
}

// ========== SECTION POUR LES GRAPHIQUES SVG ==========

function createSVGSection(svgs) {
    const section = document.createElement("div");
    section.className = "results-section svg-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📈 Graphiques';
    section.appendChild(title);

    svgs.forEach((svg, index) => {
        const card = document.createElement("div");
        card.className = "svg-card";
        card.dataset.index = index;

        const header = document.createElement("div");
        header.className = "svg-header";
        header.innerHTML = `<span class="svg-title">${svg.content?.title || 'Graphique'}</span>`;
        card.appendChild(header);

        const container = document.createElement("div");
        container.className = "svg-container";
        
        // Injection directe du SVG
        container.innerHTML = svg.content?.content || '';
        
        // Ajouter des contrôles
        const controls = document.createElement("div");
        controls.className = "svg-controls";
        
        // Créer les boutons avec des gestionnaires d'événements directs
        const downloadBtn = document.createElement("button");
        downloadBtn.innerHTML = '💾 Télécharger';
        downloadBtn.onclick = function(e) {
            e.stopPropagation();
            downloadSVG(container);
        };
        
        const copyBtn = document.createElement("button");
        copyBtn.innerHTML = '📋 Copier';
        copyBtn.onclick = function(e) {
            e.stopPropagation();
            copySVG(container);
        };
        
        const fullscreenBtn = document.createElement("button");
        fullscreenBtn.innerHTML = '🖥️ Plein écran';
        fullscreenBtn.onclick = function(e) {
            e.stopPropagation();
            toggleFullscreen(container);
        };
        
        controls.appendChild(downloadBtn);
        controls.appendChild(copyBtn);
        controls.appendChild(fullscreenBtn);
        
        card.appendChild(controls);
        card.appendChild(container);
        section.appendChild(card);
    });

    return section;
}

// ========== SECTION POUR LES STATISTIQUES AVANCÉES ==========

function createStatsSection(stats) {
    const section = document.createElement("div");
    section.className = "results-section stats-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📊 Statistiques avancées';
    section.appendChild(title);

    stats.forEach(stat => {
        const card = document.createElement("div");
        card.className = "stats-card";

        const header = document.createElement("div");
        header.className = "stats-header";
        header.innerHTML = `
            <span class="stats-name">${stat.content?.name || 'Analyse statistique'}</span>
            <span class="stats-target">cible: ${stat.content?.target || '?'}</span>
        `;
        card.appendChild(header);

        if (stat.content?.results) {
            const grid = document.createElement("div");
            grid.className = "stats-results-grid";

            Object.entries(stat.content.results).forEach(([key, value]) => {
                const item = document.createElement("div");
                item.className = "stats-result-item";

                let formattedValue = value;
                if (typeof value === 'number') {
                    formattedValue = value.toFixed(6);
                } else if (value === null || value === undefined) {
                    formattedValue = "NULL";
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? "Vrai" : "Faux";
                } else if (typeof value === 'object') {
                    const values = []
                    Object.entries(value).forEach(([key,val])=>{
                        let content = `${key} = ${val}`;
                           values.push(content);
                    });

                    formattedValue = values.join(';');
                }

                item.innerHTML = `
                    <span class="result-key">${key}:</span>
                    <span class="result-value">${formattedValue}</span>
                `;
                grid.appendChild(item);
            });

            card.appendChild(grid);
        }

        section.appendChild(card);
    });

    return section;
}


// ========== FONCTIONS EXISTANTES ==========

function createErrorSection(errors) {
    const section = document.createElement("div");
    section.className = "results-section error-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '❌ Erreurs';
    section.appendChild(title);

    errors.forEach(error => {
        const errorCard = document.createElement("div");
        errorCard.className = "error-card";

        let errorMessage = error.content;
        if (typeof error.content === 'object') {
            errorMessage = error.content.message || JSON.stringify(error.content);
        }

        errorCard.innerHTML = `
            <div class="error-line">Ligne ${error.line || '?'}</div>
            <div class="error-message">${errorMessage}</div>
        `;
        section.appendChild(errorCard);
    });

    return section;
}

function createTableSection(tables) {
    const section = document.createElement("div");
    section.className = "results-section table-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📊 Tables';
    section.appendChild(title);

    tables.forEach(table => {
        const tableCard = document.createElement("div");
        tableCard.className = "table-card";

        const tableHeader = document.createElement("div");
        tableHeader.className = "table-header";
        tableHeader.innerHTML = `
            <span class="table-name">${table.content.name || 'Table'}</span>
            <span class="table-dimensions">${table.content.shape?.[0] || 0} lignes × ${table.content.shape?.[1] || 0} colonnes</span>
        `;
        tableCard.appendChild(tableHeader);

        if (table.content.preview && table.content.preview.length > 0) {
            const tableWrapper = document.createElement("div");
            tableWrapper.className = "table-wrapper";

            const htmlTable = document.createElement("table");
            htmlTable.className = "data-preview";

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");

            const thIndex = document.createElement("th");
            thIndex.textContent = "#";
            headerRow.appendChild(thIndex);

            table.content.columns.forEach(col => {
                const th = document.createElement("th");
                th.textContent = col;
                th.title = `Type: ${table.content.types?.[table.content.columns.indexOf(col)] || 'unknown'}`;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            htmlTable.appendChild(thead);

            const tbody = document.createElement("tbody");
            table.content.preview.forEach((row, idx) => {
                const tr = document.createElement("tr");

                const tdIndex = document.createElement("td");
                tdIndex.className = "row-index";
                tdIndex.textContent = idx + 1;
                tr.appendChild(tdIndex);

                table.content.columns.forEach(col => {
                    const td = document.createElement("td");
                    let value = row[col];

                    if (value === null || value === undefined) {
                        td.textContent = "NULL";
                        td.className = "null-value";
                    } else if (typeof value === 'boolean') {
                        td.textContent = value ? "✓" : "✗";
                        td.className = value ? "boolean-true" : "boolean-false";
                    } else if (typeof value === 'number') {
                        td.textContent = value;
                        td.className = "number-value";
                    } else {
                        td.textContent = String(value);
                    }

                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            htmlTable.appendChild(tbody);

            tableWrapper.appendChild(htmlTable);
            tableCard.appendChild(tableWrapper);

            if (table.content.shape && table.content.shape[0] > table.content.preview.length) {
                const moreInfo = document.createElement("div");
                moreInfo.className = "table-more-info";
                moreInfo.textContent = `... et ${table.content.shape[0] - table.content.preview.length} lignes supplémentaires`;
                tableCard.appendChild(moreInfo);
            }
        }

        section.appendChild(tableCard);
    });

    return section;
}

function createAnalysisSection(analyses) {
    const section = document.createElement("div");
    section.className = "results-section analysis-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📈 Analyses';
    section.appendChild(title);

    analyses.forEach(analysis => {
        const analysisCard = document.createElement("div");
        analysisCard.className = "analysis-card";

        const analysisHeader = document.createElement("div");
        analysisHeader.className = "analysis-header";
        analysisHeader.innerHTML = `
            <span class="analysis-name">${analysis.content.name || 'Analyse'}</span>
            <span class="analysis-target">cible: ${analysis.content.target || '?'}</span>
        `;
        analysisCard.appendChild(analysisHeader);

        if (analysis.content.results) {
            const resultsGrid = document.createElement("div");
            resultsGrid.className = "analysis-results-grid";

            Object.entries(analysis.content.results).forEach(([key, value]) => {
                const resultItem = document.createElement("div");
                resultItem.className = "analysis-result-item";

                let formattedValue = value;
                if (typeof value === 'number') {
                    formattedValue = value.toFixed(4);
                } else if (value === null || value === undefined) {
                    formattedValue = "NULL";
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? "Vrai" : "Faux";
                } else if (typeof value === 'object') {
                    formattedValue = JSON.stringify(value);
                }

                resultItem.innerHTML = `
                    <span class="result-key">${key}:</span>
                    <span class="result-value">${formattedValue}</span>
                `;
                resultsGrid.appendChild(resultItem);
            });

            analysisCard.appendChild(resultsGrid);
        }

        if (analysis.content.options && Object.keys(analysis.content.options).length > 0) {
            const options = document.createElement("div");
            options.className = "analysis-options";
            options.innerHTML = `<span>Options: ${JSON.stringify(analysis.content.options)}</span>`;
            analysisCard.appendChild(options);
        }

        section.appendChild(analysisCard);
    });

    return section;
}

function createInfoSection(messages) {
    const section = document.createElement("div");
    section.className = "results-section info-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = 'ℹ️ Informations';
    section.appendChild(title);

    messages.forEach(msg => {
        const infoCard = document.createElement("div");
        infoCard.className = `info-card ${msg.type}`;

        let icon = '📌';
        if (msg.type === 'success') icon = '✅';
        if (msg.type === 'info') icon = 'ℹ️';

        infoCard.innerHTML = `
            <span class="info-icon">${icon}</span>
            <span class="info-message">${msg.content || msg.content?.message || JSON.stringify(msg.content)}</span>
            ${msg.line ? `<span class="info-line">ligne ${msg.line}</span>` : ''}
        `;
        section.appendChild(infoCard);
    });

    return section;
}

// ========== FONCTIONS UTILITAIRES POUR LES SVG ==========

// Fonction de téléchargement améliorée
function downloadSVG(container) {
    const svg = container.querySelector('svg');
    if (!svg) {
        console.error("SVG non trouvé");
        return;
    }

    try {
        // Cloner le SVG pour éviter les modifications
        const svgClone = svg.cloneNode(true);
        
        // S'assurer que les dimensions sont présentes
        if (!svgClone.hasAttribute('width')) {
            svgClone.setAttribute('width', '800');
        }
        if (!svgClone.hasAttribute('height')) {
            svgClone.setAttribute('height', '600');
        }
        
        const serializer = new XMLSerializer();
        const source = serializer.serializeToString(svgClone);
        
        // Ajouter la déclaration XML
        const fullSource = '<?xml version="1.0" encoding="UTF-8"?>\n' + source;
        
        const blob = new Blob([fullSource], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'chart.svg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Nettoyer
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 100);
        
    } catch (error) {
        console.error("Erreur lors du téléchargement:", error);
        alert("Erreur lors du téléchargement du SVG");
    }
}

// Fonction de copie améliorée
function copySVG(container) {
    const svg = container.querySelector('svg');
    if (!svg) {
        console.error("SVG non trouvé");
        return;
    }

    try {
        const serializer = new XMLSerializer();
        const source = serializer.serializeToString(svg);

        navigator.clipboard.writeText(source).then(() => {
            // Feedback visuel
            const btn = event?.target;
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ Copié!';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                }, 2000);
            } else {
                alert('SVG copié dans le presse-papiers !');
            }
        }).catch(err => {
            console.error("Erreur de copie:", err);
            alert("Erreur lors de la copie");
        });
    } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de la copie");
    }
}

// Fonction plein écran améliorée
function toggleFullscreen(container) {
    if (!container) return;

    if (!document.fullscreenElement) {
        // Passer en plein écran
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.webkitRequestFullscreen) { // Safari
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) { // IE/Edge
            container.msRequestFullscreen();
        }
        
        // Ajouter un bouton de sortie
        const exitBtn = document.createElement('button');
        exitBtn.className = 'fullscreen-exit-btn';
        exitBtn.innerHTML = '✖ Quitter le plein écran';
        exitBtn.style.position = 'fixed';
        exitBtn.style.top = '20px';
        exitBtn.style.right = '20px';
        exitBtn.style.zIndex = '10000';
        exitBtn.style.padding = '10px 20px';
        exitBtn.style.background = '#ff6b6b';
        exitBtn.style.color = 'white';
        exitBtn.style.border = 'none';
        exitBtn.style.borderRadius = '5px';
        exitBtn.style.cursor = 'pointer';
        exitBtn.style.fontSize = '16px';
        exitBtn.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        
        exitBtn.onclick = function() {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { // Safari
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { // IE/Edge
                document.msExitFullscreen();
            }
        };
        
        document.body.appendChild(exitBtn);
        
        // Nettoyer quand on quitte le plein écran
        const onFullscreenChange = function() {
            if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
                const btn = document.querySelector('.fullscreen-exit-btn');
                if (btn) btn.remove();
                document.removeEventListener('fullscreenchange', onFullscreenChange);
                document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
                document.removeEventListener('msfullscreenchange', onFullscreenChange);
            }
        };
        
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('msfullscreenchange', onFullscreenChange);
        
    } else {
        // Quitter le plein écran
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

// Rendre les fonctions accessibles globalement (pour les anciens appels)
window.downloadSVG = function(btn) {
    const card = btn.closest('.svg-card');
    const container = card?.querySelector('.svg-container');
    if (container) downloadSVG(container);
};

window.copySVG = function(btn) {
    const card = btn.closest('.svg-card');
    const container = card?.querySelector('.svg-container');
    if (container) copySVG(container);
};

window.toggleFullscreen = function(btn) {
    const card = btn.closest('.svg-card');
    const container = card?.querySelector('.svg-container');
    if (container) toggleFullscreen(container);
};


// Initialisation
const analysisManager = new AnalysisManager();
analysisManager.Init();
analysisManager.EventListeners();

window.analysisManager = analysisManager;
 </script>
</body>
</html> """