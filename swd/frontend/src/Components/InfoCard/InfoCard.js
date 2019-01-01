/* eslint react/jsx-no-bind: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import { Card } from 'material-ui/Card';
import { List, ListItem } from 'material-ui/List';
import Divider from 'material-ui/Divider';
import s from './InfoCard.css';

const styles = {
  listStyle: {
    backgroundColor: 'white',
    height:'72px',
    fontSize:12,
    fontFamily:'Montserrat',
    borderStyle: 'solid',
    borderColor: '#074F57',
    borderWidth: 2,
    marginBottom: 15,
    marginTop:15
  }
}

const InfoCard = (props) => {
  const { title, list } = props;
  const navigateToLink = (link) => {
    window.location = link;
  };

  const listItems = list.map(element =>
    <div key={element.title}>
      <ListItem primaryText={element.title} onClick={navigateToLink.bind(null, element.link)} style={styles.listStyle} />
      <Divider />
    </div>,

    );
  return (
    <div className={s.container}>
      <span className={s.title}> {title} </span>
      <Card>
        <List>
          {listItems}
        </List>
      </Card>
    </div>
  );
};

InfoCard.propTypes = {
  title: PropTypes.string.isRequired,
  list: PropTypes.arrayOf(PropTypes.shape(
    { title: PropTypes.string,
      link: PropTypes.string },
    )).isRequired,
};

export default InfoCard;
