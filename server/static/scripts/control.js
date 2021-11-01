document.addEventListener("DOMContentLoaded", function () {
    $('#kill-btn').on('click', function () {
        setConfirmationModal('Kill all running tasks? Istallation tasks can not be stopped', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 911 }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    $('#dismiss-confirmation-modal-btn').click();
                    showInfo('Success', 'green');
                } else {
                    showInfo('There was an error killing running tasks');
                }
            }).catch();
        }, 'Kill');
        return false;
    });

    $('#cleanup-btn').on('click', function () {
        setConfirmationModal('Delete all projects?', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 912 }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    $('#dismiss-confirmation-modal-btn').click();
                    showInfo('Success', 'green');
                } else {
                    showInfo('There was an error deleting projects');
                }
            }).catch();
        }, 'Delete');
        return false;
    });
});