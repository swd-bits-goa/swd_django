import React from 'react';
import PropTypes from 'prop-types';
import Dialog from 'material-ui/Dialog';
import RaisedButton from 'material-ui/RaisedButton';
import TextField from 'material-ui/TextField';
import Snackbar from 'material-ui/Snackbar';
import {withApollo} from 'react-apollo';
import {withRouter} from 'react-router-dom';
import Paper from 'material-ui/Paper';
import {white, cyan400, cyan500} from 'material-ui/styles/colors';
import backIcon from './back.svg';
import { withStyles } from '@material-ui/core/styles';

const styles = {
  container: {
    // zIndex: 10,
    position: 'absolute',
    // overflowX: 'hidden',
    // overflowY: 'hidden',
    top: '10%',
    right: 50,
    backgroundColor: 'white',
    width: '460px',
    height:'334px'
  },
  headerDiv: {
    backgroundColor: 'white',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-end',
    height: '100%',
  },
  header: {
    fontFamily: 'Montserrat',
    color: '#F46036',
    fontSize: 24,
    marginLeft: '15%',
    marginBottom: 0
  },
  para: {
    margin: 0,
    color: 'white',
    padding: 10
  },
  username: {
    borderStyle: 'solid',
    borderColor: '#074F57',
    fontFamily: 'Montserrat',
    color:'#074F57',
    paddingLeft: 10,
    borderWidth: 2,
    fontSize: 17,
    marginTop: 0,
    marginLeft:'15%',
    width: '70%',
    fontWeight: 'bold'
  },
  password: {
    borderStyle: 'solid',
    borderColor: '#074F57',
    fontFamily: 'Montserrat',
    color:'#074F57',
    paddingLeft: 10,
    borderWidth: 2,
    fontSize: 17,
    marginTop: 20,
    marginLeft:'15%',
    width: '70%',
    fontWeight: 'bold'
  },
  form: {
    width: '100%',
    margin: 'auto',
  },
  submitButton: {
    width: 114,
    height:55,
    marginTop: 30,
    marginLeft:'15%',
    marginBottom:30,
    display: 'inline-block'
  },
  submitButtonText: {
    fontFamily: 'Montserrat',
    color:'#074F57',
    fontSize: 22,
    fontWeight: 'bold',
    textTransform: 'capitalize'
  },
  back: {
    height: 25,
    width: 25,
    marginLeft: 15,
    alignContent: 'flex-start',
    marginTop: 15,
    padding: 5,
    paddingLeft: 0
  },
  error:{
    position:'relative',
    top:10
  },
  forgot:{
    display:'inline-block',
    color:'#7D8F91',
    fontSize:17,
    marginLeft:20,
    fontWeight:'normal',
    position:'relative',
    top:-10,
    cursor:'pointer'
  },
  authError:{
    fontSize:12,
    color:'#F46036',
    position:'absolute',
    bottom:10,
    marginLeft:'15%',
    fontWeight:'bold'
  }
}

class Login extends React.Component {

  // Validate form data
  validate(formData) {
    const fieldError = {}
    if (!formData.get("username"))
      fieldError.username = "Username required"
    if (!formData.get("password"))
      fieldError.password = "Password required"
    return fieldError
  }

  // to get token from django using REST framework
  handleSubmit(e) {

    e.preventDefault()
    let data = new FormData(this.form)
    const fieldError = this.validate(data)
    this.setState({fieldError: fieldError})

    // If we have any field errors, prevent sending login request
    if (Object.keys(fieldError).length)
      return

      // Since we're sending the request, reset field errors
    this.setState({
      fieldError: {
        username: "",
        password: ""
      }
    })

    fetch('http://localhost:8000/api-token-auth/', {
      method: 'POST',
      body: data
    }).then(res => {
      res
        .json()
        .then(res => {
          if (res.token) {
            localStorage.setItem('token', res.token)
            this.props.login()
            // No need to refresh, component will rerender
            // Request LoginModal close
            this.goHome();

            // Reset Apollo's cache store so that it can refetch all active queries
            this
              .props
              .client
              .resetStore()
          }
          // Error handling
          if (res.non_field_errors) {
            this.setState({nonFieldError: res.non_field_errors[0]})
          }

        })
    }).catch(err => {
      this.setState({nonFieldError: "Could Not Authenticate!"})
    })
  }

   goBack = () => {
     this.props.history.goBack();
   }

   goHome = () => {
     this.props.history.push("/");
   }

  static propTypes = {
    login: PropTypes.func.isRequired
  };

  //  TODO: Convert form into a controlled React component

  state = {
    fieldError: {
      username: "",
      password: ""
    },
    nonFieldError: ""
  }

  render() {
    // Refers to the preceding private route that might have redirected to login
  let privateRoute = this.props.location.state;
      return (
        <div
          style={styles.container}
        >
        {
      privateRoute
      ? <Snackbar
          open={true}
          message={"You must log in to view " + privateRoute.from.pathname.slice(1) + "!"}
          autoHideDuration={4000}
        />

      : null
        }
          <Paper zDepth={1} style={styles.headerDiv}>
            <div style={{
              marginBottom: 'auto'
            }}>
            </div>
            <h2 style={styles.header}>My Account</h2>
          <div>
            <form
              ref={ref => (this.form = ref)}
              onSubmit={e => this.handleSubmit(e)}
              id="form"
              style={styles.form}>
              <span style={styles.authError}>{this.state.nonFieldError}</span>
              <br/>
              <TextField
                hintText="Username"
                name="username"
                autoComplete="username"
                style={styles.username}
                underlineStyle={{display: 'none'}}
                errorText={this.state.fieldError.username}
                errorStyle = {styles.error}
                />
                <br/>
              <TextField
                hintText="Password"
                name="password"
                type="password"
                autoComplete="current-password"
                errorText={this.state.fieldError.password}
                errorStyle = {styles.error}
                style={styles.password}
                fullWidth = {true}
                underlineStyle={{display: 'none'}}
                />
              <br/>

              <RaisedButton
                label="Login"
                backgroundColor="#FFBE57"
                type="submit"
                form="form"
                labelStyle = {styles.submitButtonText}
                style={styles.submitButton}/>

               <h2 style={styles.forgot}>Forgot Passsword?</h2>

            </form>
          </div>
          </Paper>
        </div>
      );
  }
}

export default withRouter(withApollo(Login));
