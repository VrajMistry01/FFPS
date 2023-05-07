function validateForm() {
    var source = document.getElementById("Source").value;
    var destination = document.getElementById("Destination").value;
    var dep_time = document.getElementById("Dep_Time").value;
    var arrival_time = document.getElementById("Arrival_Time").value;

    if (source === destination) {
        alert("Source and destination cannot be the same.");
        return false;
    }

    if (dep_time === arrival_time) {
        alert("Departure and arrival times cannot be the same.");
        return false;
    }

    const departureTime = new Date(document.getElementById("Dep_Time").value);
    const arrivalTime = new Date(document.getElementById("Arrival_Time").value);

    if (arrivalTime <= departureTime) {
        alert("Arrival time must be later than departure time");
        focusOnArrivalTime();
        return false;
    }

    return true;

}

function focusOnArrivalTime() {
    document.getElementById("Arrival_Time").focus();
}