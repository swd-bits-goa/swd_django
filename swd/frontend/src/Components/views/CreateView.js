// not required, just a template to recieve data

import React from 'react'
import { gql, graphql } from 'react-apollo'

const query = gql`
{
  currentUser {
    id
    username
  }
}
`

class CreateView extends React.Component {
  componentWillUpdate(nextProps) {
    if (!nextProps.data.loading && nextProps.data.currentUser === null) {
      window.location.replace('/login/')
    }
  }

  render() {
    let { data } = this.props
    if (data.loading) {
      return <div>Loading...</div>
    }
    return (<div>CreateView</div>);
  }
}

CreateView = graphql(query)(CreateView)
export default CreateView