
export const DataCore = {
    sessionName: "",
    payload: { tables: {}, analysis: {} },

    update(name, data) {
        this.sessionName = name;
        this.payload = data;
    },

    async save() {
        await pywebview.api.save_as(this.payload);
    }
};