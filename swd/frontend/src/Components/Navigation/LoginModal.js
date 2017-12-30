
import React from 'react';
import PropTypes from 'prop-types';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import TextField from 'material-ui/TextField';
import {withApollo} from 'react-apollo';


class LoginModal extends React.Component {

  // Validate form data
  validate(formData) {
    const fieldError = {}
    if(!formData.get("username")) fieldError.username = "Username required"
    if(!formData.get("password")) fieldError.password = "Password required"
    return fieldError
  }


  // to get token from django using REST framework
  handleSubmit(e) {

    e.preventDefault()
    let data = new FormData(this.form)
    const fieldError = this.validate(data)
    this.setState({ fieldError: fieldError})
      
    // If we have any field errors, prevent sending login request
    if (Object.keys(fieldError).length) return;

    fetch('http://localhost:8000/api-token-auth/', {
      method: 'POST',
      body: data,
    })
      .then(res => {
        res.json().then(res => {
          if (res.token) {
            localStorage.setItem('token', res.token)
            this.props.login()
            // No need to refresh, component will rerender
            // Request LoginModal close
            this.props.onRequestClose()
            
            // Reset Apollo's cache store so that it can refetch all active queries
            this.props.client.resetStore()
          }
          // Error handling
          if (res.non_field_errors)
          {
            this.setState({ nonFieldError: res.non_field_errors[0]})
          }

        })
      })
      .catch(err => {
        this.setState({ nonFieldError: "Oops! Network error"})
      })
  }

  static propTypes = {
    open: PropTypes.bool.isRequired, // Handles modal state
    // Closure to allow child component to handle state data
    onRequestClose: PropTypes.func.isRequired,
    login: PropTypes.func.isRequired
  };

//  TODO: Convert form into a controlled React component 

  state = {
    fieldError : {
      username : "",
      password : ""
    },
    nonFieldError : "",
  }

  render() {
    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.props.onRequestClose}
      />,
      <FlatButton
        label="Login"
        primary
        keyboardFocused
        type="submit"
        form="form"
      />,
    ];

    return (
      <div>
        <Dialog
          title="Log In"
          actions={actions}
          modal={true}
          open={this.props.open}
          onRequestClose={this.props.onRequestClose}
        >
          Username same as BITS mail. Use your LDAP Authentication password to login.

          <form
          ref={ref => (this.form = ref)}
          onSubmit={e => this.handleSubmit(e)}
          id="form"
          >
          <span style={{ color: 'red' }}>{ this.state.nonFieldError }</span>
          <br/> 
          <TextField
          floatingLabelText = "Username" name = "username" autoComplete = "username" 
          errorText={this.state.fieldError.username} />
          <br/> 
          <TextField
          floatingLabelText="Password" name="password" type="password" 
          autoComplete="current-password" errorText={this.state.fieldError.password}/> 
          <br/> 
        </form>
        </Dialog>
      </div>
    );
  }
}

export default withApollo(LoginModal);
