function createTestsList(tests){
    var list = document.createElement('div');
    list.classList.add('list-group');
    for (var i = 0; i < tests.length; i++)  (function (i) {
        var item = document.createElement('a');
        item.setAttribute('id', tests[i].id);
        item.classList.add('list-group-item');
        item.classList.add('list-group-item-action');
        var labelClass = ''
        if(tests[i].status == 1){
            labelClass = "green"
        }
        if(tests[i].status == 2){
            labelClass = "orange"
        }
        const template = `
            <div class="form-check">
            <input
                class="form-check-input"
                type="checkbox"
                value=""
                id="flexCheckDefault-${tests[i].id}"
            />
            <label class="test-label ${labelClass}">
                ${tests[i].id}
            </label>
            </div>
        `;
        item.innerHTML = template;
        // handle check box events
        $(item).find('input').change(function() {
 
            if (this.checked) {
                $('#delete').prop("disabled",false);
                // add test to selected tests
                selectedTests.push(tests[i].id);
                
            } else {
                // remove test from selected tests
                const index = selectedTests.indexOf(tests[i]);
                if (index > -1) {
                    selectedTests.splice(index, 1);
                }
                if (selectedTests.length < 1){
                    $('#delete').prop("disabled",true);
                }
            }
        });

        $(item).find('label').on('click', function(){
            window.location.href = '/test/'+tests[i].id;
        });
        list.appendChild(item);
    })(i);
    return list;
}

var selectedTests = [];

window.onload = function () {
    fetch('/tests').then(data => data.json()).then(data => {
        if (data.success){
            const tests = data.tests;
            $('#content').append(createTestsList(tests));
        }
    }).catch();

    const deleteBtn = $('#delete');
    deleteBtn.prop("disabled",true);
    //handle delete button
    deleteBtn.on("click", function(){
        let formData = new FormData();
        formData.append('ids', JSON.stringify(selectedTests));
        setConfirmationModal('Are you sure you want to delete these test?', function() {
             fetch('/delete', { method: 'POST', body: formData }).then(data => {
                $('#dismiss-confirmation-modal-btn').click();
                location.reload();
            }).catch();
        });
        return false;
    });

}   