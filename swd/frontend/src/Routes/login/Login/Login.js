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

const styles = {
  container: {
    // zIndex: 10,
    position: 'fixed',
    // overflowX: 'hidden',
    // overflowY: 'hidden',
    top: 0,
    backgroundColor: 'white',
    width: '100%',
    height: '100%'
  },
  headerDiv: {
    backgroundColor: cyan500,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-end',
    height: '40%',
    margin: 6
  },
  header: {
    fontFamily: 'Open Sans',
    color: 'white',
    paddingLeft: 10,
    paddingBottom: 0,
    marginBottom: 0
  },
  para: {
    margin: 0,
    color: 'white',
    padding: 10
  },
  username: {
    fontSize: 25,
    marginTop: 0
  },
  password: {
    fontSize: 25
  },
  form: {
    width: '92%',
    margin: 'auto',
    marginTop: -5
  },
  submitButton: {
    width: '100%',
    marginTop: 30
  },
  back: {
    height: 25,
    width: 25,
    marginLeft: 15,
    alignContent: 'flex-start',
    marginTop: 15,
    padding: 5,
    paddingLeft: 0
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
      this.setState({nonFieldError: "Oops! Network error"})
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
              <img src={backIcon} style={styles.back} onClick={this.goBack}/>
            </div>
            <h2 style={styles.header}>Welcome!</h2>
            <p style={styles.para}>Username same as BITS mail.<br/>
              Use your LDAP Authentication password to login.</p>
          </Paper>
          <div>

            <form
              ref={ref => (this.form = ref)}
              onSubmit={e => this.handleSubmit(e)}
              id="form"
              style={styles.form}>
              <span style={{
                color: 'red'
              }}>{this.state.nonFieldError}</span>
              <br/>
              <TextField
                floatingLabelText="Username"
                name="username"
                autoComplete="username"
                errorText={this.state.fieldError.username}
                style={styles.username}
                fullWidth={true}/>
              <br/>
              <TextField
                floatingLabelText="Password"
                name="password"
                type="password"
                autoComplete="current-password"
                errorText={this.state.fieldError.password}
                style={styles.password}
                fullWidth={true}/>
              <br/>

              <RaisedButton
                label="Login"
                backgroundColor={cyan400}
                labelColor={white}
                type="submit"
                form="form"
                style={styles.submitButton}/>
            </form>
          </div>
        </div>
      );
  }
}

export default withRouter(withApollo(Login));
