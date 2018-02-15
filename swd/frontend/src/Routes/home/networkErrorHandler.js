import React from "react";

function networkErrorHandler (FallbackComponent, Component) {
  class NetworkErrorHandler extends React.Component {
    constructor () {
      super()
      // Construct the initial state
      this.state = {
        hasError: false
      }
    }

    componentWillMount (error, info) {

      for (var data in this.props)
      {
          if(data.error || !data)
          {
            // Update state if error happens
            this.setState({ hasError: true })
          }
          
      }  
      

    //   // Report errors
    //   errorCallback(error, info, this.props)
    }

    render () {
      // if state contains error we render fallback component
      if (this.state.hasError) {
        return (
          <FallbackComponent />
        )
      }

      return <Component {...this.props} />
    }
  }
  NetworkErrorHandler.displayName = `networkErrorHandler(${Component.displayName})`
  return NetworkErrorHandler
}

const fallback = props => (
    <h1>Something Went Wrong</h1>
)

export default networkErrorHandler(fallback);