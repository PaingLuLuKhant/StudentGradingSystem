
    // containers
    let studentContainer = document.querySelector(".StudentsContainer")
    let gradeContainer = document.querySelector(".GradesContainer")
    
    const filterStudentsButton = document.getElementById("filterStudentsButton");
    
    filterStudentsButton.addEventListener("click", function () {
        // Get the selected batch value
        const selectedBatch = document.getElementById("batch").value;
    
        // Get the selected major(s)
        const cseMajorChecked = document.getElementById("cseMajor").checked;
        const eceMajorChecked = document.getElementById("eceMajor").checked;
        const bothMajorChecked = document.getElementById("bothMajor").checked;
    
        if (cseMajorChecked) {
            showSelectedBatchInfo(selectedBatch, "cse")
        }
        else if (eceMajorChecked) {
            showSelectedBatchInfo(selectedBatch, "ece")
        }
        else if (bothMajorChecked) {
            showSelectedBatchInfo(selectedBatch)
        }
    
        // Close the modal
        let modalElement = document.getElementById('batch-select')
        var modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
    });
    async function showSelectedBatchInfo(batch, major = null) {
        hideAllContainers();
    
        studentContainer.innerHTML = "";
        let div = createTableStructure();
        studentContainer.appendChild(div);
    
        let table = document.querySelector('table');
        let searchStudentBtn = document.querySelector(".searchStudentPanel .search");
    
        let clearButton = document.querySelector(".searchStudentPanel .btnclear");
        let studentTableContainer = document.querySelector(".StudentsContainer .ta")
    
        clearButton.addEventListener("click", function () {
            searchInput.value = "";
            clearTable(studentTableContainer)
        });
    
    
    
        let searchInput = document.querySelector(".searchStudentPanel input");
    
        // Add event listener for Enter key press on search input
        searchInput.addEventListener('keypress', async function (event) {
            if (event.key === 'Enter') {
                clearTable(table);
                let searchText = document.querySelector(".searchStudentPanel input").value;
                console.log(searchText);
                let data = await getSpecificStudent(searchText, batch)
                displayDataInTable(data, div);
            }
        });
    
        searchStudentBtn.addEventListener("click", async function () {
            clearTable(table);
            let searchText = document.querySelector(".searchStudentPanel input").value;
            console.log(searchText);
            let data = await getSpecificStudent(searchText, batch)
            displayDataInTable(data, div);
        });
    
        let data = major ? await getSpecificStudent(major, batch) : await getAllStudent(batch)
        displayDataInTable(data, div);
    
    
        let cgpaFilterButton = document.getElementById("cgpaFilterButton");
    
        cgpaFilterButton.addEventListener("click", async () => {
            clearTable(table);
            let selectedValue = document.getElementById("cgpaFilter").value;
            console.log("hello");
            let data = major ? await getStudentByCgpaAndMajor(selectedValue, batch, major) : await getStudentByCgpa(selectedValue, batch)
            displayDataInTable(data, div);
        })
    
        

        let exportButton = document.getElementById('export_excel_button');
        if (exportButton) {
            exportButton.addEventListener('click', async () => {
                console.log('Sending export request');
                // Send an AJAX request to the Django view that handles the export
                const isExportRequest = true;

                function getCookie(name) {
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            const cookie = cookies[i].trim();
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
            
                const csrftoken = getCookie('csrftoken');
            
                fetch('/excel_export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken // Use the CSRF token from the cookie
                    },
                    body: JSON.stringify({
                        buttonPressed: true, // This will be sent to the backend
                        isExportRequest: isExportRequest
                    })
                })
                .then(response => {
                    if (response.ok) {
                        // If the response is OK, create a Blob from the response and create a link to download it
                        response.blob().then(blob => {
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = 'student_list.xlsx';
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                        });
                    } else {
                        // Handle the error
                        alert('Failed to export data.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        };
        studentContainer.style.display = "block";
    }
    
    function createTableStructure() {
        let div = document.createElement("div");
        div.classList.add("DataforStudentsContainer");
        div.innerHTML = `
            <div class="searchStudentPanel">
                <div class="inputcontainer">
                    <div class="search-box">
                        <input type="text" placeholder="Search for student...">
                        <button class="btnclear" type="button">&times;</button>
                    </div>
                    <button class="search"><i class="fas fa-search"></i></button>
    
                    <div class="filterSection">
                        <label for="cgpaFilter" style="font-size:18px;">Filter by CGPA:</label>
                        <select id="cgpaFilter" class="cgpaFilter">
                            <option value="1">Under 1</option>
                            <option value="2" selected>Under 2</option>
                            <option value="3">Under 3</option>
                        </select>
                        <button class="applyFilter" id="cgpaFilterButton" style="margin-right: 10px;">Apply</button>
                    </div>
                    <div class="export_excel">
                        <button id="export_excel_button">Export Student List</button>
                    </div>
                </div>
    
                <table class="ta">
                <tr>
                    <th>Name</th>
                    <th>Roll Number</th>
                    <th>CGPA</th>
                </tr>
            </table>
            </div>
    
        `;
        return div;
    }
    
    async function getAllStudent(batch) {
        const response = await fetch(`http://127.0.0.1:8000/all_students/${batch}`)
        const data = await response.json()
        return data;
    }
    async function getSpecificStudent(input, batch) {
        const response = await fetch(`http://127.0.0.1:8000/specific_student/${input}/?batch=${batch}`)
        const data = await response.json()
        return data;
    }
    async function getStudentByCgpa(input, batch) {
        const response = await fetch(`http://127.0.0.1:8000/get_student_by_cgpa/${input}/?batch=${batch}`)
        const data = await response.json()
        return data;
    }
    async function getStudentByCgpaAndMajor(selectedValue, batch, major) {
        const response = await fetch(`http://127.0.0.1:8000/get_student_by_cgpa_and_major/${selectedValue}/?batch=${batch}&major=${major}`)
        const data = await response.json()
        return data;
    }
    
    function displayDataInTable(data, div) {
    
        console.log(data);
    
        data.students.sort((a, b) => {
            // Extract the department from the roll number
            const deptA = a.roll_number.split('-')[2].substring(0, 3);
            const deptB = b.roll_number.split('-')[2].substring(0, 3);
    
            // Compare departments
            if (deptA !== deptB) {
                return deptA > deptB ? 1 : -1;
            }
    
            // If departments are the same, compare roll numbers
            // Extract the numeric part of the roll number for comparison
            const rollNumberA = parseInt(a.roll_number.split('-')[3], 10);
            const rollNumberB = parseInt(b.roll_number.split('-')[3], 10);
    
            return rollNumberA - rollNumberB;
        });
    
        let table = div.querySelector('table');
    
        data.students.forEach((student, index) => {
            let row = table.insertRow();
            let cell1 = row.insertCell(0);
            let cell2 = row.insertCell(1);
            let cell3 = row.insertCell(2);
    
            cell1.innerText = student.name || '';
    
            let cgpa = parseFloat(student.cgpa);
    
            let roll_number = student.roll_number
    
            let rollNumberColor = cgpa < 2 ? '#c30010' : '#005EB8';
    
            cell2.innerHTML = `<span onclick="switchFromStudentToGrade('${roll_number}')" 
                                style="text-decoration: none; color: ${rollNumberColor};
                                cursor: pointer;">${student.roll_number}</span>` || '';
    
            let roundedCgpa = Math.round(cgpa * 100) / 100;
    
            cell3.innerHTML = `<span onclick="switchFromStudentToGrade('${roll_number}')" 
                                style="text-decoration: none; color: ${rollNumberColor};
                                cursor: pointer;">${roundedCgpa}</span>` || '';
    
    
    
            row.style.backgroundColor = index % 2 === 0 ? "lightgrey" : "white";
        });
        studentContainer.appendChild(div)
    }
    function switchFromStudentToGrade(roll_number) {
        hideAllContainers()
        getStudentGrades(roll_number)
        searchInput.value = "";
        gradeContainer.style.display = "block"
    }
    function clearTable(table) {
        // Remove all rows except the first one (header row)
        let rows = table.querySelectorAll('tr:not(:first-child)');
        rows.forEach(row => row.remove());
    }
    
    RecommendContainer = document.querySelector(".RecommendContainer")
    function hideAllContainers() {
        studentContainer.style.display = "none"
        gradeContainer.style.display = "none"
        RecommendContainer.style.display = "none"
    }
    
    // grade button
    let gradeButton = document.getElementById("gradeButton")
    let gradesTablesContainer = document.querySelector(".gradesTablesContainer");
    
    gradeButton.addEventListener("click", () => {
        hideAllContainers()
        gradesTablesContainer.innerHTML = ""
        gradeContainer.style.display = "block";
    
        let searchInput = searchStudentPanelInGrades.querySelector("input");
        searchInput.value = "";
    })
    
    let searchStudentPanelInGrades = document.querySelector(".searchStudentPanelInGrades"); // from js 213
    let searchButton = document.querySelector(".search-button");
    
    // Get references to the input field and clear button
    let searchInput = document.querySelector(".search-input");
    let clearButton = document.querySelector(".btn-clear");
    
    // Add event listener for Enter key press on search input
    searchInput.addEventListener('keypress', async function (event) {
        if (event.key === 'Enter') {
    
            let searchText = searchStudentPanelInGrades.querySelector("input").value;
            console.log(searchText);
            getStudentGrades(searchText)
            // ... existing code to perform the search and update gradesDiv ...
        }
    });
    
    clearButton.addEventListener("click", function () {
        searchInput.value = "";
        gradesTablesContainer.innerHTML = ""
    });
    
    searchButton.addEventListener("click", function () {
        let searchText = searchStudentPanelInGrades.querySelector("input").value;
        console.log(searchText);
        getStudentGrades(searchText)
        // ... existing code to perform the search and update gradesDiv ...
    });
    
    async function getStudentGrades(input) {
        console.log(input);
        const response = await fetch(`http://127.0.0.1:8000/getStudentGrades/${input}/`);
        const data = await response.json();
    
        if (!data || !data.grades) {
            alert('Student does not exist');
        } else {
            displayGradesInTables(data);
        }
    }
    
    RecommendContainer = document.querySelector(".RecommendContainer")
    
    
    
    function displayGradesInTables(data) {
        gradesTablesContainer.innerHTML = ""
    
        console.log(data)
    
        let cgpa = parseFloat(data.cgpa);
        let roundedCgpa = Math.round(cgpa * 100) / 100;
        const cgpaDiv = document.createElement('div');
    
        cgpaDiv.className = 'cgpa-display';
        cgpaDiv.innerHTML = `   <table>
                                    <tr>
                                        <th> Name </th>
                                        <th> Roll Number </th>
                                        <th> CGPA </th>
                                    </tr>
                                    <tr>
                                        <th> ${data.name}</th>
                                        <th> ${data.roll_num}</th>
                                        <th> ${roundedCgpa}</th>
                                    </tr>
                                </table>   
                                <br>     
                                <p style="font-size : 20px; font-weight:bold; text-align:center; align-items:center;">Accumulated Credits : ${data.total_credit_points}`
    
        gradesTablesContainer.appendChild(cgpaDiv);
    
        if (data.cgpa < 2) {
    
            let div = document.createElement('div');
            div.classList.add("recommendationDiv");
    
            div.innerHTML = `<button style="float: right; margin-right: 20px; margin-top: -90px;border: none; font-size : 23px ; 
            border-radius : 10px; cursor: pointer;  background-color: #007bff; color: white;" title ="See Details";>
            <i class="fa-solid fa-arrow-right"></i></button>`;
    
    
            gradesTablesContainer.appendChild(div);
    
            recommendButtons = document.querySelectorAll(".recommendationDiv button")
    
            recommendButtons.forEach(button => {
                button.addEventListener("click", () => {
                    gradeRecommendation(cgpaDiv, data)
                });
            });
        }
    
    
        const tablesContainer = document.createElement('div');
        tablesContainer.className = 'tables-container';
    
    
        const semesterIds = data.grades.map(grade => parseInt(grade.sem_id.substring(1)));

    // Find the largest semester ID
    const largestSemesterId = semesterIds.length > 0 ? Math.max(...semesterIds) : 0;

    // Track the number of tables added in this row
    let tablesInRow = 0;
    let rowContainer = null;

    // Iterate over each semester
    for (let semesterIndex = 0; semesterIndex < largestSemesterId; semesterIndex++) {
        const semesterId = `S${semesterIndex < 9 ? '0' : ''}${semesterIndex + 1}`;
        const hasGradesForSemester = data.grades.some(grade => grade.sem_id === semesterId);

        if (hasGradesForSemester) {
            // Create table for semester with grades
            const tableContainer = document.createElement('div');
            tableContainer.className = 'table-container';

            const semesterName = `Semester ${semesterIndex + 1}`;
            const semesterHeader = document.createElement('h4');
            semesterHeader.innerHTML = `<u>${semesterName}</u>`;
            tableContainer.appendChild(semesterHeader);

            // Create the table
            const table = document.createElement('table');
            table.className = 'table';

            // Create table headers
            const thead = table.createTHead();
            const headers = ['No', 'Course Name', 'Grade'];
            const headerRow = thead.insertRow();
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });

            // Create table body
            const tbody = table.createTBody();
            let rowCounter = 1;
            data.grades.forEach(grade => {
                if (grade.sem_id === semesterId) {
                    const row = tbody.insertRow();
                    row.insertCell().textContent = rowCounter++;
                    ['course_name', 'grade'].forEach(key => {
                        const cell = row.insertCell();
                        cell.textContent = grade[key];
                    });
                }
            });

            // Get the SGPA for the current semester
            const sgpa = data.grades.find(grade => grade.sem_id === semesterId)?.sgpa;

            // Add table footer for SGPA
            const tfoot = table.createTFoot();
            const footerRow = tfoot.insertRow();

            const footerCell1 = footerRow.insertCell();
            const footerCell2 = footerRow.insertCell();
            const footerCell3 = footerRow.insertCell();

            footerCell1.style.border = "none";
            footerCell2.textContent = `SGPA`;
            footerCell3.textContent = sgpa ? sgpa.toFixed(2) : "0";

            tableContainer.appendChild(table);

            // Append the table container to the row container
            if (tablesInRow === 0) {
                rowContainer = document.createElement('div');
                rowContainer.className = 'row-container';
            }
            rowContainer.appendChild(tableContainer);
            tablesInRow++;

            // If three tables added, append row to the tables container and reset tablesInRow
            if (tablesInRow === 3) {
                tablesContainer.appendChild(rowContainer);
                tablesInRow = 0;
            }
        }
    }

    // If there are remaining tables in the last row, append it to the tables container
    if (tablesInRow > 0) {
        tablesContainer.appendChild(rowContainer);
    }

    gradesTablesContainer.appendChild(tablesContainer);
}
    
// recommendation system 

let cgpaDivInRecommend = document.querySelector(".cgpaDivInRecommend")
let okButtonDiv = document.querySelector(".okButtonDiv")
let gradeWeightDiv = document.querySelector(".gradeWeightDiv")

function gradeRecommendation(cgpaDiv, data) {
    hideAllContainers()
    cgpaDivInRecommend.innerHTML = ""
    okButtonDiv.innerHTML = ""
    gradeWeightDiv.innerHTML = ""
    cgpaDivInRecommend.appendChild(cgpaDiv)

    let div = document.createElement("div")
    div.innerHTML = `
    <div style="display: flex; align-items: center;">
        <h6 style="margin-left: 220px;padding :5px;">How many Credit Points will this student be offered in the next semester?</h6>
        <input type="text" pattern="\\d*" id="creditCount" style="margin-right: 10px; margin-top: -5px; padding:5px; border: 1px solid #ccc; border-radius: 4px;">
        <span style="margin-left: 10px;"></span>
        <button id="okButton" style="background-color: #007bff; color: white; border: none; padding: 5px 10px; margin-top: -2px; border-radius:   4px; cursor: pointer;">OK</button>
    </div>
        `;

    okButtonDiv.appendChild(div)
    RecommendContainer.style.display = "block"

    okButton = document.getElementById("okButton")
    okButton.addEventListener("click", async () => {
        creditCount = document.getElementById("creditCount").value
        const response = await fetch(`http://127.0.0.1:8000/recommendation/${creditCount}/?roll_num=${data.roll_num}`);
        const recommendData = await response.json();
        console.log(recommendData);
        createGradeWeightsTable(recommendData.grade_weights);
        createRecommendTable(recommendData.average_grade_point,recommendData.credit_point_offered_next_sem,recommendData.current_total_credit_points
            );
    })
    creditCountInput = document.getElementById("creditCount")
    creditCountInput.addEventListener('keypress', async function (event) {
        if (event.key === 'Enter') {
            creditCount = document.getElementById("creditCount").value
            const response = await fetch(`http://127.0.0.1:8000/recommendation/${creditCount}/?roll_num=${data.roll_num}`);
            const recommendData = await response.json();
            console.log(recommendData);
            createGradeWeightsTable(recommendData.grade_weights);
            createRecommendTable(recommendData.average_grade_point,recommendData.credit_point_offered_next_sem,recommendData.current_total_credit_points
                );
        }
    });

}
function createGradeWeightsTable(gradeWeights) {
    let gradeWeightDiv = document.querySelector(".gradeWeightDiv")
    gradeWeightDiv.innerHTML = ""

    const table = document.createElement('table');
    table.style.marginTop = '20px';
    table.style.borderCollapse = 'collapse';
    table.style.width = '70%';
    table.style.marginLeft = 'auto';
    table.style.marginRight = 'auto';


    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    for (const grade of Object.keys(gradeWeights)) {
        const headerCell = headerRow.insertCell();
        headerCell.textContent = grade;
        headerCell.style.border = '1px solid black'; // Add border to each header cell
        headerCell.style.padding = '2px';
        headerCell.style.width = '10%';
        headerCell.style.textAlign = 'center';
    }
    const tbody = table.createTBody();
    const row = tbody.insertRow();

    for (const weight of Object.values(gradeWeights)) {
        const cell = row.insertCell();
        cell.textContent = weight;
        cell.style.border = '1px solid black';
        cell.style.padding = '2px';
        cell.style.width = '10%';
        cell.style.textAlign = 'center';
    }
    gradeWeightDiv.appendChild(table);
}
function createRecommendTable(average_grade_point, credit_point_offered_next_sem, current_total_credit_points) {
    let table = document.createElement('table');
    table.style.marginTop = '20px';
    table.style.borderCollapse = 'collapse'; // Ensure borders are collapsed
    table.style.width = '70%';
    table.style.marginLeft = 'auto';
    table.style.marginRight = 'auto';

    let tbody = document.createElement('tbody');

    // Current Total Credit Points
    let row1 = document.createElement('tr');
    let cell1_1 = document.createElement('td');
    cell1_1.textContent = 'Current Total Credit Points';
    cell1_1.style.textAlign = 'center';
    cell1_1.style.border = '1px solid black';
    let cell1_2 = document.createElement('td');
    cell1_2.textContent = current_total_credit_points;
    cell1_2.style.textAlign = 'center';
    cell1_2.style.border = '1px solid black';
    row1.appendChild(cell1_1);
    row1.appendChild(cell1_2);
    tbody.appendChild(row1);

    // Credit Point Offered Next Semester
    let row2 = document.createElement('tr');
    let cell2_1 = document.createElement('td');
    cell2_1.textContent = 'Credit Point Offered Next Semester';
    cell2_1.style.textAlign = 'center';
    cell2_1.style.border = '1px solid black';
    let cell2_2 = document.createElement('td');
    cell2_2.textContent = credit_point_offered_next_sem;
    cell2_2.style.textAlign = 'center';
    cell2_2.style.border = '1px solid black';
    row2.appendChild(cell2_1);
    row2.appendChild(cell2_2);
    tbody.appendChild(row2);

    let row3 = document.createElement('tr');
    let cell3_1 = document.createElement('td');
    cell3_1.textContent = 'Total Credit Points After Next Semester';
    cell3_1.style.textAlign = 'center';
    cell3_1.style.border = '1px solid black';
    let cell3_2 = document.createElement('td');
    cell3_2.textContent = credit_point_offered_next_sem + current_total_credit_points;
    cell3_2.style.textAlign = 'center';
    cell3_2.style.border = '1px solid black';
    row3.appendChild(cell3_1);
    row3.appendChild(cell3_2);
    tbody.appendChild(row3);

    // Average Grade Point
    let row4 = document.createElement('tr');
    let cell4_1 = document.createElement('td');
    cell4_1.textContent = 'Average Grade Point Needed to Reach CGPA 2';
    cell4_1.style.textAlign = 'center';
    cell4_1.style.border = '1px solid black';
    let cell4_2 = document.createElement('td');
    cell4_2.textContent = average_grade_point.toFixed(2); // Format to 2 decimal places
    cell4_2.style.textAlign = 'center';
    cell4_2.style.border = '1px solid black';
    row4.appendChild(cell4_1);
    row4.appendChild(cell4_2);
    tbody.appendChild(row4);

    table.appendChild(tbody);

    // Append the table to the body or another container element
    // Assuming gradeWeightDiv is defined elsewhere in your code
    
    gradeWeightDiv.appendChild(table);
}
    

    







    // Select all elements with class 'dropdown-item' within the '.dropdown-menu'
    let dropdownItems = document.querySelectorAll('.dropdown-menu .dropdown-item');

    dropdownItems.forEach((currentItem) => {
        currentItem.addEventListener('click', () => {
    
            let clickedText = currentItem.innerText.trim();
    
            if (clickedText === 'Dashboard') {
                console.log('Dashboard clicked');
            }
            else if (clickedText === 'Profile') {
                console.log('Profile clicked');
            }
            else if (clickedText === 'Log out') {
                console.log('Log out clicked');
            }
        });
    });