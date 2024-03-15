
responseTextforStudent = document.getElementById("responseTextforStudent")
// excel.js
function submitFormData(formId) {
    responseTextforStudent.innerHTML = ""
    const formElement = document.getElementById(formId);
    const fileInput = formElement.querySelector('input[type="file"]');
    const file = fileInput.files[0];

    // Check if a file is selected
    if (!file) {
        alert('Please select a file to upload.');
        return;
    }

    // Check if the file is an Excel file (.xls or .xlsx)
    const validExtensions = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    if (!validExtensions.includes(file.type)) {
        alert('Invalid file type. Please upload an Excel file (.xls or .xlsx).');
        return;
    }

    const formData = new FormData(formElement);

    fetch('/excel_import/', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        console.log('Success:', data);
        
        // responseTextforStudent.innerHTML = `
        //  ${data.message} <i class="fa-solid fa-check" style="color: #008000; font-size:  24px; margin-right:  5px;"></i> ${data.updated_text[0]}
        // <button id="seeDetailsButton" style="border: none; text-decoration: none; background: none; cursor: pointer;" title ="See Details">
        // <i class="fa-solid fa-circle-info" style="color: black; font-size:  20px; margin-left:  5px;"></i></button>                                                
        //     `;
        responseTextforStudent.innerHTML = `
        ${data.message} <i class="fa-solid fa-check" style="color: #008000; font-size:  24px; margin-right:  5px;"></i>
        Database is updated for ${data.success} rows and ${data.error} rows were skipped.
        
                                                       
            `;

        // seeDetailsButton = document.getElementById("seeDetailsButton")
        // seeDetailsButton.addEventListener("click", () =>{
        //     openLogsModal(data)
        // })
    }).catch(error => {
        console.error('Error:', error);
    });
}

// Attach event listeners to the submit buttons of each form
document.getElementById('excelUploadFormStudents').addEventListener('submit', function(event) {
    event.preventDefault();
    submitFormData('excelUploadFormStudents');

});

document.getElementById('excelUploadFormCourses').addEventListener('submit', function(event) {
    event.preventDefault();
    submitFormData('excelUploadFormCourses');
});

document.getElementById('excelUploadFormEnrollment').addEventListener('submit', function(event) {
    event.preventDefault();
    submitFormData('excelUploadFormEnrollment');
});
document.getElementById('excelUploadFormSemesters').addEventListener('submit', function(event) {
    event.preventDefault();
    submitFormData('excelUploadFormSemesters');
});