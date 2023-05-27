import  React,  {useState}  from  'react';
import  Form  from  'react-bootstrap/Form';
import  Container  from  'react-bootstrap/Container';
import  Button  from  'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

const  Signup  =  props  =>  {
    const  [username,  setUsername]  =  useState("");
    const  onChangeUsername  =  e  =>  {
        const  username  =  e.target.value;
        setUsername(username);
    }
    const  signup  =  ()  =>  {
        props.signup(username);
    }
    return(
    <Container fluid >
                        
        <Form>
            <Form.Group>
                <Row className="justify-content-md-center ml-10 h-200">
                    <Col xs lg="2">
                        <Form.Label>Please signup</Form.Label>
                    </Col>
                    <Col  xs lg="3">
                        <Form.Control
                            className="float-right" 
                            type="text"
                            placeholder="Enter  username"
                            value={username}
                            onChange={onChangeUsername}
                        />
                    </Col>    
                    <Col xs lg="2">
                        <Button  variant="primary" className='float-right mt-20' onClick={signup}>Sign  Up</Button>
                    </Col>  
                </Row>
            </Form.Group>

        </Form>
   
    </Container>
  )
}

export  default  Signup;