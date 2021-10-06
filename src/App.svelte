<script>
  function execute_hotp(devices)
  {
    // Only run inside frames from duosecurity.com
    if (!window.location.href.includes('duosecurity.com'))
      return;

    const hotp = new jsOTP.hotp();

    // Check to see if any stored devices matches devices in the dropdown
    devices.forEach((data, _idx) => {
      let found = false;
      const options = document.querySelector('select[name="device"]').options;
      Array.prototype.forEach.call(options, (a) => {if (a.label.includes(data.device)) found=true});
      if (!found)
        return;
      const hmacCode = hotp.getOtp(data.secret, data.counter);
      const device = document.evaluate(`//option[contains(., "${data.device }")]`, document).iterateNext();
      device.selected = true;
      const index = options.selectedIndex;
      document.querySelector(`input[name='passcode'][data-index=${device.value}]`).value = hmacCode;
      document.querySelectorAll('button[id="passcode"]')[index].click();
      data.counter += 1;
    });

    chrome.storage.sync.set({'devices': devices}, {}); // Save counter
  }

  let device_array = [];
  chrome.storage.sync.get(['devices'], function(result) {
    if (result.devices.length)
      device_array = result.devices;

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.scripting.executeScript(
        {
          target: {tabId: tabs[0].id, allFrames: true},
          files: ['build/jsOTP.min.js']
        },
        () => {
          chrome.scripting.executeScript({
            target: {tabId: tabs[0].id, allFrames: true},
            func: execute_hotp,
            args: [device_array]
          });
        }
      );
    });
  });

  let add_new = false;
  let nick, link;
  function confirm() {
    if (!nick || !link) {
      alert('You must enter both fields!');
      return;
    }
    else if (!link.includes('duosecurity.com')) {
      alert('Link is incorrect!');
      return;
    }

    let host, code;
    if (link.includes("qr?value=")) {
      const qrlink = decodeURIComponent(link.split("qr?value=")[1]);
      host = atob(qrlink.split('-')[1]);
      code = qrlink.split('-')[0].replace('duo://', '');
    }
    else {
      host = link.split('/')[2].replace('m-', 'api-');
      code = link.split('/')[4];
    }
    const url = `https://${host}/push/v2/activation/${code}`;

    fetch(url, {method: "POST"})
    .then(response => response.json())
    .then(json => {
      device_array.push({
        device : nick,
        secret : json['response']['hotp_secret'],
        counter : 0,
      });
      chrome.storage.sync.set({'devices': device_array}, {});

      add_new = false;
    })
  }

  function remove(idx) {
    device_array = device_array.filter((e, i) => i !== idx);
    chrome.storage.sync.set({'devices': device_array}, {});
  }
</script>

<main>
  <button on:click={() => {add_new = true}}>Add new device</button>
  {#if !add_new}
    {#each device_array as device, idx}
      <div style="display: flex; align-items: center;">
        <h2>{device.device}</h2>
        <div class='close' on:click={() => remove(idx)}><svg width="36" height="36" viewBox="0 0 24 24"><path d="M18.4 4L12 10.4L5.6 4L4 5.6L10.4 12L4 18.4L5.6 20L12 13.6L18.4 20L20 18.4L13.6 12L20 5.6L18.4 4Z"></path></svg></div>
      </div>
    {/each}
  {:else}
    <div style='display:flex; flex-direction: column;'>
      <p style="margin: 0;">Add a new device with a unique nickname to your Duo dashboard. Then input the nickname and the activation/QR code link here. The QR code link can be found by right clicking the QR code, and selecting "copy image address."</p>
      <label for="link">Nickname:</label>
      <input bind:value={nick} type="text" name="nick" id="nick">
      <label for="link">Link:</label>
      <input bind:value={link} type="text" name="link" id="link">
      <div style="margin: 0 auto; text-align: center;">
        <button style="margin: 0 0.5em;" on:click={confirm}>Confirm</button>
        <button style="margin: 0 0.5em;" on:click={() => {add_new = false}}>Cancel</button>
      </div>
    </div>
  {/if}
</main>

<style>
  main {
    min-width: 20em;
    min-height: 25em;
    display: flex;
    flex-direction: column;
    padding: 0.5em;
  }

  button {
    font-size: 1.5em;
    font-weight: bold;
  }

  h2 {
    margin: .75em .5em;
  }

  label {
    margin: .5em 0;
    font-size: 1.25em;
  }

  input {
    margin-bottom: 0.5em;
    width: 100%;
  }

  .close {
    margin-left: auto;
    cursor: pointer;
    fill: red;
  }
</style>