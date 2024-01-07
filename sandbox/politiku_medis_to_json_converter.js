// Go to e.g., https://politikumedis.lt/seimo-nari%C5%B3-balsavim%C5%B3-rezultatai/d%C4%97l-x-w-ir-q-raid%C5%BEi%C5%B3-naudojimo-asmens-dokumentuose
// and run this script

function generateJSONFromTable() {
  var table = document.querySelector('table');
  var data = [];

  for (var i = 1; i < table.rows.length; i++) {
    var row = table.rows[i];
    var cols = row.cells;

    var vote = 'Unknown';
    if (cols[2].hasAttribute('bgcolor') && cols[2].getAttribute('bgcolor') === 'green') {
      vote = 'Už';
    } else if (cols[3].hasAttribute('bgcolor') && cols[3].getAttribute('bgcolor') === 'red') {
      vote = 'Prieš';
    } else if (cols[4].hasAttribute('bgcolor') && cols[4].getAttribute('bgcolor') === 'yellow') {
      vote = 'Susilaikė';
    } else if (cols[5].hasAttribute('bgcolor') && cols[5].getAttribute('bgcolor') === 'black') {
      vote = 'Registravosi';
    } else if (cols[6].hasAttribute('bgcolor') && cols[6].getAttribute('bgcolor') === 'grey') {
      vote = 'Nedalyvavo';
    }

    var member = {
      'Seimo narys(-ė)': cols[0].innerText.trim(),
      vote: vote,
    };
    data.push(member);
  }

  return JSON.stringify(data, null, 2); // Convert array to JSON string
}

console.log(generateJSONFromTable());
