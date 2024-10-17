declare global {
  interface WindowEventMap {
    "eip6963:announceProvider": CustomEvent;
  }
}

/* This function is responsible for connecting to the provider using `eth_requestAccounts`
   The `wallet` object is passed as an argument to the function indicating the detail of tis type 
   as the argument type.
*/

const getParams = async () => {
     const url = `${window.location.origin}/params`;

        // Make a GET request to the new URL
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Check if the response is OK (status in the range 200-299)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Parse the response as text or JSON (depending on your needs)
        const data = await response.json();
        return data
}

const getDone = async (txHash : string) => {
     const url = `${window.location.origin}/done`;
        
        const txHashParam = new URLSearchParams({txHash})
        const response = await fetch(url + '?' + txHashParam.toString(), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
             
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await response.json();
        
}

const connectWithProvider = async (wallet: EIP6963AnnounceProviderEvent['detail']) => {
  try {
    
    // get account
    const accounts: string[] = await wallet.provider
      .request({ method: 'eth_requestAccounts' }) as string[]

    //get tx params
    const{ to, value, data, chainId } = await getParams()
    const tx = {
        to, value, data, chainId,
        from: accounts[0]
    }
    
    await wallet.provider.request({
      method: "eth_sendTransaction",
      params: [tx],
    })
    .then((txHash: unknown) => {
        // send txhash to server
        getDone(txHash as string)
    })
    .catch((error: any) => {
        getDone('rejected')
        console.error(error)
    });
  

  } catch (error: any) {
    
    console.error("Failed to connect to provider:", error);
  }
};

/* In this approach, we've opted for a simplified (over mapping and joining an entire block of HTML).
   We're directly passing the `event.detail` object to the `connectWithProvider` function when a provider is announced.
   `connectWithProvider` is then called when the button is clicked.

   This method seems to be more straightforward and less error-prone 
   as it directly passes the required data without attempting to stringify data objects which led to 
   circular reference errors due to the object's structure. 
*/


export function listProviders(element: HTMLDivElement) {

  window.addEventListener('eip6963:announceProvider',
    // Event handler function: second argument called to perform work when the event occurs. 
    (event: EIP6963AnnounceProviderEvent) => {
      const button = document.createElement('button');

      // use string interpolation to set the button's innerHTML
      button.innerHTML = `
        <img src="${event.detail.info.icon}" alt="${event.detail.info.name}" />
        <div>${event.detail.info.name}</div>`;
      
      // Add an onClick event listener to the button that calls the `connectWithProvider` function
      button.onclick = () => connectWithProvider(event.detail);
      element.appendChild(button);
    }
  );

  /*
    dispatch custom event on `window` object used to notify other parts of the dapp that a provider 
    is being requested, and any event listeners set up to listen for this event, respond accordingly.
  */
  window.dispatchEvent(new Event("eip6963:requestProvider"));
}

