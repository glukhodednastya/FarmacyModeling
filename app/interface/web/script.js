eel.expose(showError)
function showError(err) {
    alert(err)
}

eel.expose(showProgress)
function showProgress(progress) {
    document.getElementById('paramsView').style.display = 'none'
    document.getElementById('progressView').style.display = 'flex'
    document.getElementById('resultsView').style.display = 'none'
    document.getElementById('progressBar').value = progress
    document.getElementById('progressBar').innerText = `${progress}%`
}

eel.expose(showResults)
function showResults(profit, ordersDelivered, ordersInProgress, stockPrice, logs, couriersLoad, utilizationLoss) {
    console.log(couriersLoad, utilizationLoss)
    document.getElementById('profitValue').innerText = `${profit.toFixed(2)}руб`
    if (profit > 0) {
        document.getElementById('profitValue').classList.remove('loss')
        document.getElementById('profitValue').classList.add('profit')
    } else {
        document.getElementById('profitValue').classList.add('loss')
        document.getElementById('profitValue').classList.remove('profit')
    }
    document.getElementById('ordersDeliveredValue').innerText = `${ordersDelivered}`
    document.getElementById('ordersInProgressValue').innerText = ordersInProgress === 0 ? '—' : (
        ordersInProgress === 1 ? `${ordersInProgress} день` : (
            ordersInProgress < 5 ? `${ordersInProgress} дня` : `${ordersInProgress} дней`))
    document.getElementById('stockPriceValue').innerText = `${stockPrice.toFixed(2)}руб`
    document.getElementById('courierLoad').innerText = (
        couriersLoad === -1 ? '—' :
            `${Math.round(couriersLoad.toFixed(2) * 100)} %`)
    document.getElementById('utilizationLoss').innerText = `${utilizationLoss.toFixed(2)}руб`

    printLogs(logs)

    document.getElementById('paramsView').style.display = 'none'
    document.getElementById('progressView').style.display = 'none'
    document.getElementById('resultsView').style.display = 'grid'
}

eel.expose(printLogs)
function printLogs(logs) {
    let newLogsContent = ''
    for (let record of logs) {
        let logsList = ''
        logsList += `<div>`
        logsList += `<h3>Период моделирования: ${document.getElementById('date_from').value} - ${document.getElementById('date_to').value}</h3>`
        logsList += `<h3>${record.date}</h3>`
        for (let log of record.logs) {
            logsList += `
                <div>
                    <span>${log.msg}</span>
                    ${
                        log.profit > 0 ?
                        `<b class="profit">+${log.profit.toFixed(2)}руб</b>`:
                        (
                            log.profit === 0 ?
                            `` :
                            `<b class="loss">${log.profit.toFixed(2)}руб</b>`
                        )
                    }
                </div>
            `
        }
        logsList += `</div>`
        newLogsContent += logsList
    }
    document.getElementById('logsList').innerHTML = newLogsContent
}

let medicines = [
    {
        'name': 'Ибупрофен',
        'code': '123',
        'medication_size': 50,
        'retail_price': 300
    },
    {
        'name': 'Анальгин',
        'code': '234',
        'medication_size': 100,
        'retail_price': 100
    },
    {
        'name': 'Ношпа',
        'code': '345',
        'medication_size': 100,
        'retail_price': 150
    },
    {
        'name': 'Аспирин',
        'code': '456',
        'medication_size': 100,
        'retail_price': 50
    },
    {
        'name': 'Парацетамол',
        'code': '567',
        'medication_size': 100,
        'retail_price': 100
    },
    {
        'name': 'Нурофен',
        'code': '678',
        'medication_size': 100,
        'retail_price': 300
    }
]

function drawMedicines() {
    let newMedicinesListContent = ''
    let i = 0
    for (let med of medicines) {
        newMedicinesListContent += `
            <div class="medicine-card">
                <div class="med_name">
                        <label>Название</label>
                        <input type="text" value="${med.name}" disabled>
                </div>
                <div class="med_code">
                    <label>Баркод</label>
                    <input type="text" value="${med.code}" disabled>
                </div>
                <div class="med_portion">
                    <label>Размер порции, мг</label>
                    <input type="number" value="${med.medication_size}" disabled>
                </div>
                <div class="med_price">
                    <label>Оптовая цена, руб</label>
                    <input type="number" value="${med.retail_price}" disabled>
                </div>
                <div class="add_del_btn" onclick="removeMedicine(${i})">
                    <div class="button button_red">Удалить</div>
                </div>
            </div>
        `
        i += 1
    }
    newMedicinesListContent += `
        <div class="medicine-card">
            <div class="med_name">
                <label>Название</label>
                <input type="text" id="newMedicineName">
            </div>
            <div class="med_code">
                <label>Баркод</label>
                <input type="text" id="newMedicineCode">
            </div>
            <div class="med_portion">
                <label>Размер порции, мг</label>
                <input type="number" id="newMedicinePotionSize">
            </div>
            <div class="med_price">
                <label>Оптовая цена, руб</label>
                <input type="number" id="newMedicinePrice">
            </div>
            <div class="add_del_btn">
                <div class="button button_green" id="addMedicineButton">Добавить</div>
            </div>
        </div>
    `
    document.getElementById('medicinesList').innerHTML = newMedicinesListContent
    document.getElementById('addMedicineButton').addEventListener('click', addMedicine)
}
function addMedicine() {
    document.getElementById('newMedicineName').style.border = '1px solid lightgray'
    document.getElementById('newMedicineCode').style.border = '1px solid lightgray'
    document.getElementById('newMedicinePotionSize').style.border = '1px solid lightgray'
    document.getElementById('newMedicinePrice').style.border = '1px solid lightgray'


    let valid = true
    if (document.getElementById('newMedicineName').value === '') {
        document.getElementById('newMedicineName').style.border = '1px solid red'
        valid = false
    }

    if (document.getElementById('newMedicineCode').value === '') {
        document.getElementById('newMedicineCode').style.border = '1px solid red'
        valid = false
    }

    if (
        document.getElementById('newMedicinePotionSize').value === ''
        || parseFloat(document.getElementById('newMedicinePotionSize').value) <= 0
    ) {
        document.getElementById('newMedicinePotionSize').style.border = '1px solid red'
        valid = false
    }
    if (
        document.getElementById('newMedicinePrice').value === ''
        || parseFloat(document.getElementById('newMedicinePrice').value) <= 0
    ) {
        document.getElementById('newMedicinePrice').style.border = '1px solid red'
        valid = false
    }


    if (valid) {
        medicines.push({
            'name': document.getElementById('newMedicineName').value,
            'code': document.getElementById('newMedicineCode').value,
            'medication_size': document.getElementById('newMedicinePotionSize').value,
            'retail_price': document.getElementById('newMedicinePrice').value
        })
        drawMedicines()
    }
}
function removeMedicine(i) {
    medicines.splice(i, 1)
    drawMedicines()
}

eel.expose(highlightErrors)
function highlightErrors(errors) {
    for (let field_name of errors) {
        document.getElementById(field_name).style.border = '1px solid red'
    }
}

function getNextDay() {
    console.log(medicines)
    let data = {
        'date_from': document.getElementById('date_from').value,
        'date_to': document.getElementById('date_to').value,
        'budget': document.getElementById('budget').value,
        'margin': document.getElementById('margin').value,
        'discount': 50,
        'supply_size': document.getElementById('supply_size').value,
        'couriers_amount': document.getElementById('couriers_amount').value,
        'working_hours': document.getElementById('working_hours').value,
        'courier_salary': document.getElementById('salary').value,
        'medicines': medicines,
    }

    console.log(data)
    eel.get_next_day(data)
}

document.getElementById('startModelingButton').onclick = getNextDay
document.getElementById('getNextDay').onclick = getNextDay

document.getElementById('runUntilComplete').onclick = () => {
    eel.run_until_complete()
    document.getElementById('runUntilComplete').style.display = 'none'
    document.getElementById('getNextDay').style.display = 'none'
}

document.getElementById('startAgain').onclick = () => {
    eel.start_again();
    window.location.reload()
}

window.onload = () => drawMedicines()
