import React from "react";
import PropTypes from "prop-types";

function networkErrorHandler(LoadingComponent, FallbackComponent, Component) {
  class NetworkErrorHandler extends React.Component {
    constructor(props) {
      super(props)
      // Construct the initial state
      this.state = {
        isLoading: true,
        hasError: false
      }
    }

    // Flow of props passed to GrapQL HoC: loading: true, no data loading : false,
    // data is available and good
    componentWillReceiveProps(nextProps) {
      // Need to correct workflow of query checking
      // Also need to identify queries from normal props
      console.log("HoC view of queries passed to it", nextProps)
      for (var key in nextProps) {
        // Iterate through each query to check network state
        let query = nextProps[key]
        console.log("Going through query " + key)
        // Need to also consider the case of '!query'
        if (query.error) {
          // Update state if error happens
          this.setState({hasError: true})
          console.log("Error while loading data!")
          // We also have to differentiate between GraphQL and network errors
          console.log(query.error)
          break;
        } else if (query.loading) {
          this.setState({isLoading: true})
          console.log("Data is loading")
        } 
        // else if(!(query[key])) {
        //   this.setState({hasError: true})
        //   console.log("Sorry! Data could not be loaded.")
        // }
        else {
          this.setState({isLoading: false})
          console.log("Data has been succesfully loaded!")
        }
      }

      //     if(data.error || !data)     {       // Update state if error happens
      //  this.setState({ hasError: true })     } }

    }

    // This is meant for client-side errors!
    componentDidCatch(error, info) {
    // Display fallback UI
    this.setState({ hasError: true });
    // You can also log the error to an error reporting service
    // logErrorToMyService(error, info);
    console.log("Error in JS", info);
  }

    // Report errors if any
// Here's a good link to follow:
// https://codeburst.io/catching-exceptions-using-higher-order-components-in-reac
// t-16-b8a401853a10
    //errorCallback(error, info, this.props)

    render() {
      // if state contains error we render fallback component
      if (this.state.hasError) {
        // Errors can be further split into GraphQL and Network errors
        return (<FallbackComponent/>)
      } else if (this.state.isLoading) {
        return (<LoadingComponent/>)
      } else {
        return (<Component {...this.props}/>)
      }
    }
  }
  NetworkErrorHandler.displayName = `networkErrorHandler(${Component.displayName})`
  return NetworkErrorHandler
}

export default networkErrorHandler;
