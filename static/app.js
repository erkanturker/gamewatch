async function populateModal(
  title,
  savings,
  price,
  salesPrice,
  store,
  gameId,
  metaCriticScore,
  steamRatingPercent,
  steamRatingText,
  steamRatingCount
) {
  const data = await fetchGameInfo(gameId);
  updateCheapestEver(data, price);
  updateCheapestCurrentStore(data, store);
  updateModalContent(
    title,
    price,
    metaCriticScore,
    steamRatingPercent,
    steamRatingText,
    steamRatingCount
  );
}

async function fetchGameInfo(gameId) {
  const response = await fetch(`/gameInfo/${gameId}`);
  return response.json();
}

function updateCheapestEver(data, price) {
  const cheapestPriceEver = data.cheapestPriceEver.price;
  const cheapastEverElement = document.getElementById("cheapastEver");
  if (cheapestPriceEver >= price) {
    cheapastEverElement.innerText = "Yes";
    cheapastEverElement.classList.add("text-success");
  } else {
    cheapastEverElement.innerText = "No";
    cheapastEverElement.classList.add("text-danger");

    const date = new Date(data.cheapestPriceEver.date * 1000);
    const formattedDate = new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(date);

    document.getElementById(
      "cheapastPriceEver"
    ).innerText = `$${cheapestPriceEver} on ${formattedDate}`;
  }
}

function updateCheapestCurrentStore(data, store) {
  let cheapestPriceFromDeals = Infinity;
  let cheapestStoreIDFromDeals = null;

  data.deals.forEach((deal) => {
    const price = parseFloat(deal.price);
    if (price < cheapestPriceFromDeals) {
      cheapestPriceFromDeals = price;
      cheapestStoreIDFromDeals = deal.storeID;
    }
  });

  const isCheapestCurrentStoreElement = document.getElementById(
    "isCheapestCurrentStore"
  );
  if (cheapestStoreIDFromDeals == store) {
    isCheapestCurrentStoreElement.innerText = "Yes";
    isCheapestCurrentStoreElement.classList.add("text-success");
  } else {
    isCheapestCurrentStoreElement.innerText = "No";
    isCheapestCurrentStoreElement.classList.add("text-danger");
    document.getElementById(
      "cheapestCurrentStore"
    ).innerText = `StoreID: ${cheapestStoreIDFromDeals}   $${cheapestPriceFromDeals}`;
  }
}

function updateModalContent(
  title,
  price,
  metaCriticScore,
  steamRatingPercent,
  steamRatingText,
  steamRatingCount
) {
  document.getElementById("gameModalLabel").innerText = `${title} $${price}`;
  document.getElementById("metaCriticScore").innerText = metaCriticScore;
  document.getElementById("steamRatingText").innerText = steamRatingText;
  document.getElementById("steamRatingCount").innerText = steamRatingCount;
  document.getElementById("steamRatingPercent").innerText = steamRatingPercent;
}
