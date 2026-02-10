function addMedicine() {
    const div = document.createElement("div");
    div.innerHTML = `
        <br>
        <label>Medicine</label>
        <input type="text" name="medicine[]" required>

        <label>Quantity</label>
        <input type="number" name="quantity[]" min="1" required>

        <label>Days</label>
        <input type="number" name="days[]" placeholder="e.g. 30" min="1" required>
    `;
    document.getElementById("medicines").appendChild(div);
}