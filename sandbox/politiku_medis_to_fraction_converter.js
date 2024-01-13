// Go to e.g., https://politikumedis.lt/seimo-nari%C5%B3-balsavim%C5%B3-rezultatai/d%C4%97l-x-w-ir-q-raid%C5%BEi%C5%B3-naudojimo-asmens-dokumentuose
// and run this script

function generateJSONFromTable() {
  const table = document.querySelector('table');
  const mp_to_fraction_map = {};

  for (var i = 1; i < table.rows.length; i++) {
    var row = table.rows[i];
    var cols = row.cells;
    const mp_name = cols[0].innerText.trim();
    mp_to_fraction_map[mp_name] = cols[1].innerText.trim();
  }

  return JSON.stringify(mp_to_fraction_map);
}

console.log(generateJSONFromTable());
