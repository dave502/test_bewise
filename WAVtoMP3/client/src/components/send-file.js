import { ChangeEvent, useState } from 'react';
import Button from 'react-bootstrap/Button';

function FileUploadSingle(props) {
  const [file, setFile] = useState();
  const base64 = require('base-64');


  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (!file) {
      return;
    }
    const data = new FormData();
    data.append('file', file);
    data.append('filename', file.name);

    fetch(props.url, {
      method: 'POST',
      files: {"file":(file.name, file)},
      headers: {
        "Authorization": "Basic " + base64.encode(props.user + ":" + props.uuid)
      },
      body: data
    })
    .then(res => { 
      if(!res.ok) {
        return res.json().then(text => { throw new Error(text.message) })
      }
      else res.json().then((data) => {console.log(data.url);props.set_link(data.url)})})
    .catch((err) => {console.log(err.message); props.set_err(err.message)});
  };
  

  return (
    <div className="mb-3">
        <label className="form-label ">Upload file with "wav" format</label>
        <div className="input-group mb-3">
            <input className="form-control" type="file" id="formFile" onChange={handleFileChange} ></input>
            <Button className="float-right" onClick={handleUploadClick}>Upload</Button>
        </div>
    </div>
  );
}

export default FileUploadSingle;