import React, { Component } from "react";
import {BrowserRouter as Router, Route, Switch, Link, Redirect } from "react-router-dom";
import { ApolloProvider } from "react-apollo";
import { ApolloClient } from "apollo-client";
import { HttpLink } from "apollo-link-http";
import { ApolloLink, concat } from "apollo-link";
import { InMemoryCache } from "apollo-cache-inmemory";
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import Home from "./Routes/home/Home";
import AboutSWD from "./Routes/aboutSWD/AboutSWD";
import Layout from "./Components/Layout";
import logo from "./logo.svg";
import PropTypes from "prop-types";
import injectTapEventPlugin from "react-tap-event-plugin";
import Search from './Components/Search/Search.js';
import Profile from "./Routes/profile/Profile";
import Login from "./Routes/login/Login";

// react-tap-event-plugin provides onTouchTap() to all React Components.
// It's a mobile-friendly onClick() alternative for components in Material-UI,
// especially useful for the buttons.
injectTapEventPlugin();

//Sets the material-ui theme colors and settings
const muiTheme = getMuiTheme({userAgent: navigator.userAgent});

const link = new HttpLink({
  uri: "http://localhost:8000/graphql",
  credentials: "same-origin"
});

const authMiddleware = new ApolloLink((operation, next) => {
  operation.setContext(({ headers = {} }) => ({
    headers: {
      ...headers,
      authorization: `JWT ${localStorage.getItem("token") || null}`
    }
  }));

  return next(operation);
});

const client = new ApolloClient({
  link: concat(authMiddleware, link),
  cache: new InMemoryCache()
});

const PrivateRoute = ({ render, loggedIn, ...rest}) => (
  <Route {...rest} render={props => (
loggedIn ?
    render()
    : <Redirect to="/login"/> 

  )} />
);

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      //Check if we're already logged in when starting the app.
      // However this is an offline method
      loggedIn: localStorage.getItem('token') ? true : false , 

      latestNews: [
        {
          title: "Winner of Aditya Birla Group scholarship 2017",
          link: "blah"
        },
        {
          title: "Important notice regarding MCN scholarship",
          link: "blah"
        }
      ]
    };


  }

  getChildContext() {
    return {loggedIn: this.state.loggedIn}
  }

  login = () => {
    this.setState({ loggedIn: true})
  }

  logout = () => {
    this.setState({ loggedIn: false})
  }

  render() {

    return (
      // apollo interfacing
      <ApolloProvider client={client}>
        <MuiThemeProvider muiTheme={muiTheme}>
        <Router>
          <Switch>
            {/* // Might need to add routing behaviour to take care of expired sessions */}
            <Route
              path="/login"
              render={() => (
                <Login login={this.login}/>
              )}
            />
            <Route
              path="/search/:query?"
                component={({ match })=>(
                  <Layout isLoggedIn={this.state.loggedIn} logout={this.logout} searchMode={true}>
                    <Search searchQuery={match.params.query}/>
                  </Layout>
                )}/>
             <PrivateRoute
              path="/profile"
              loggedIn={this.state.loggedIn}
              render={() => (
                <Layout isLoggedIn={this.state.loggedIn} logout={this.logout} searchMode={false}>
                <Profile/>
                </Layout>
              )}
            />
            <Route
              path="/aboutSWD"
              render={() => (
                <Layout isLoggedIn={this.state.loggedIn} logout={this.logout} searchMode={false}>
                <AboutSWD/>
                </Layout>
              )}
            />
            <Route
               path="/"
              component={() => (
                <Layout isLoggedIn={this.state.loggedIn} logout={this.logout} searchMode={false}>
                  <Home news={this.state.latestNews} />
                </Layout>
              )}
            /> 
          </Switch>
        </Router>
        </MuiThemeProvider>
      </ApolloProvider>
            
    );
  }
}

App.childContextTypes = {
  loggedIn: PropTypes.bool
}

export default App;
