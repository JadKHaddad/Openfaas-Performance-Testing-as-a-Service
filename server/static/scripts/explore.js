function createTestsList(tests) {
    var list = document.createElement('div');
    list.classList.add('list-group');
    for (var i = 0; i < tests.length; i++)  (function (i) {
        var item = document.createElement('a');
        item.setAttribute('id', tests[i].id);
        item.classList.add('list-group-item');
        item.classList.add('list-group-item-action');
        var labelClass = ''
        if (tests[i].status == 1) {
            labelClass = "green"
        }
        if (tests[i].status == 2) {
            labelClass = "orange"
        }
        if (tests[i].valid === false) {
            labelClass = "red"
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
        $(item).find('input').change(function () {

            if (this.checked) {
                $('#delete').prop("disabled", false);
                // add test to selected tests
                selectedTests.push(tests[i].id);
            } else {
                // remove test from selected tests
                const index = selectedTests.indexOf(tests[i].id);
                if (index > -1) {
                    selectedTests = selectedTests.splice(index + 1, 1);
                }
                if (selectedTests.length < 1) {
                    $('#delete').prop("disabled", true);
                }
            }
        });

        $(item).find('label').on('click', function () {
            window.location.href = '/test/' + tests[i].id;
        });
        list.appendChild(item);
    })(i);
    return list;
}

var selectedTests = [];

document.addEventListener("DOMContentLoaded", function () {
    function callBack(data) {
        if (data.success) {
            const tests = data.tests;
            $('#content').append(createTestsList(tests));
        }
    }
    if (DIRECT) {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 6 }) }).then(data => data.json()).then(data => {
            callBack(data);
        }).catch();
    } else {
        fetch('/tests').then(data => data.json()).then(data => {
            callBack(data);
        }).catch();
    }

    const deleteBtn = $('#delete');
    deleteBtn.prop("disabled", true);
    //handle delete button
    deleteBtn.on("click", function () {
        function callBack() {
            $('#dismiss-confirmation-modal-btn').click();
            location.reload();
        }
        setConfirmationModal('Are you sure you want to delete these test?', function () {
            if (DIRECT) {
                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 7, ids: selectedTests }) }).then(data => data.json()).then(data => {
                    callBack();
                }).catch();
            } else {
                let formData = new FormData();
                formData.append('ids', JSON.stringify(selectedTests));
                fetch('/delete', { method: 'POST', body: formData }).then(data => {
                    callBack();
                }).catch();
            }
        });
        return false;
    });
});