import React, { Component } from "react";
import {BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import { ApolloProvider } from "react-apollo";
import { ApolloClient } from "apollo-client";
import { HttpLink } from "apollo-link-http";
import { ApolloLink, concat } from "apollo-link";
import { InMemoryCache } from "apollo-cache-inmemory";
import Home from "./Routes/home/Home";
import Layout from "./Components/Layout";
import logo from "./logo.svg";
import PropTypes from "prop-types";
import injectTapEventPlugin from "react-tap-event-plugin";
import Search from './Components/Search/Search.js';

// react-tap-event-plugin provides onTouchTap() to all React Components.
// It's a mobile-friendly onClick() alternative for components in Material-UI,
// especially useful for the buttons.
injectTapEventPlugin();

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

// networkInterface.use([
// {
//   applyBatchMiddleware(req, next) {
//     if (!req.options.headers) {
//       req.options.headers = {}How
//     }

//     const token = localStorage.getItem('token')
//       ? localStorage.getItem('token')
//       : null
//     req.options.headers['authorization'] = `JWT ${token}`
//     next()
//   },
// },
// ])

const client = new ApolloClient({
  link: concat(authMiddleware, link),
  cache: new InMemoryCache()
});

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loggedIn: localStorage.getItem('token') ? true : false , 
      //Check if we're already logged in when starting the app
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

  static childContextTypes = {
    loggedIn: PropTypes.bool
  }


  getChildContext = () => ({
    loggedIn: this.state.loggedIn
  })

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
        <Router>
          <Switch>
            <Route
              path="/search/:query?"
                component={({ match })=>(
                  <Layout isLoggedIn={this.state.loggedIn} login={this.login} logout={this.logout} searchMode={true}>
                    <Search searchQuery={match.params.query}/>
                  </Layout>
                )}/>
            <Route
              exact path="/"
              component={() => (
                <Layout isLoggedIn={this.state.loggedIn} login={this.login} logout={this.logout} searchMode={false}>
                  <Home news={this.state.latestNews} />
                </Layout>
              )}/>
          </Switch>
        </Router>
      </ApolloProvider>
    );
  }
}

export default App;
