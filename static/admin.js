var totalUserNumberElement = document.getElementById("totalUserNumber");
var totalUserNumber = 0;
var targetTotalUserNumber = document.getElementById("total").innerText;
var totalIncrementStep = Math.ceil(targetTotalUserNumber / ((1.5 * 1000) / 50));
var totalIncrementInterval = setInterval(function () {
  totalUserNumber += totalIncrementStep;
  if (totalUserNumber >= targetTotalUserNumber) {
    totalUserNumber = targetTotalUserNumber;
    clearInterval(totalIncrementInterval);
  }
  totalUserNumberElement.textContent = totalUserNumber;
}, 50);

