//npm install react-bootstrap bootstrap
//npm install base-64

import  'bootstrap/dist/css/bootstrap.min.css';
import  React,  {useState}  from  'react';
import FileUploadSingle from './components/send-file';
import Signup from './components/signup';
import  Container  from  'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Navbar from 'react-bootstrap/Navbar';


function App() {
  const  [user,  setUser]  =  React.useState(localStorage.getItem('user'));
  const  [uuid,  setUUID]  =  React.useState(localStorage.getItem('uuid'));
  const  [error, setError]  =  React.useState('');
  const  [link,  setLink]  =  React.useState('');
  const api_url = 'http://localhost:5000/api/'; //process.env.REACT_APP_API_URL;//

  async function signup(user  =  null){  //  default  user  to  null
    await fetch(api_url + 'signup/' + user, {method: 'POST',})
    .then(response => response.json())
    .then(data  =>{
      setUser(data.unique_name);
      setUUID(data.uuid);
      localStorage.setItem('user', data.unique_name); 
      localStorage.setItem('uuid',  data.uuid);
      setError('');
      setLink('');
    })
    .catch(  e  =>{
        console.log('signup',  e);
        setError(e.toString());
    });
  }


  async  function  logout(){
    setUser('');
    setUUID('');
    setLink('');
    clear_link();
    localStorage.setItem('user',  '');
    localStorage.setItem('uuid',  '');
  }

  async  function  update_link(link){
    setLink(link);
    setError('');
  }


  async  function  set_error(error){
    setLink('');
    setError(error);
  }

  async  function  clear_link(){
    setLink('');
    setError('');
  }

  return (
    <div className="App">
      <header className="App-header">
      <Navbar bg="dark" variant="dark" className="align-middle">
        <Container>
          <Navbar.Brand href="#home" >
          🎵 WAV ⇨ MP3
          </Navbar.Brand>
        </Container>
      </Navbar>
      </header>
      <Container className="align-middle p-5" >
        {user ? (
                  <Container className="col-8 text-center">
                      <Button variant='link' className='float-right mb-3' onClick={logout}>Logout  ({user})</Button>
                      <FileUploadSingle user={user} uuid={uuid} url={api_url + 'convert'} set_link={update_link} set_err={set_error} />
                  </Container>                 
                )  :  (
                <Signup signup={signup}/>
          )}
          {link ? (
                  <Container className="col-8 text-center">
                      <Button variant='link' className='float-right mb-3' href={link} onClick={clear_link}>Download MP3 </Button>
                  </Container>                 
                )  :  (
                <></>
          )}
           {error ? (
                <Container className="col-8 text-center">
                <div className="alert alert-primary text-center" role="alert">
                           {error}
                </div>
                </Container> 

                )  :  (
                <></>
          )}
      </Container>
    </div>

  );
}


export default App;
