function createTestsList(tests, project_name) {
    var list = document.createElement('div');
    list.classList.add('list-group');
    for (var i = 0; i < tests.length; i++)  (function (i) {
        var item = document.createElement('a');
        item.setAttribute('id', tests[i]);
        item.classList.add('list-group-item');
        item.classList.add('list-group-item-action');
        const template = `
            <label class="test-label">
                ${tests[i]}
            </label>
        `;
        item.innerHTML = template;


        $(item).find('label').on('click', function () {
            window.location.href = '/project/' + project_name + '/' +  tests[i];
        });
        list.appendChild(item);
    })(i);
    return list;
}

document.addEventListener("DOMContentLoaded", function () {
    const project_name = document.getElementById('project-name').innerText;

    // get all locust scripts of this test

    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 4 , project_name:project_name}) }).then(data => data.json()).then(data => {
        if (data.success) {
            const tests = data.locust_scripts;
            $('#content').append(createTestsList(tests, project_name));
        }
    }).catch(function(){
        showInfo('Could not connect to server','red');
    });
});