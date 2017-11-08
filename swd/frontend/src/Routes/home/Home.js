
/* eslint no-unused-vars:0 */

import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardActions, CardHeader, CardMedia, CardTitle, CardText } from 'material-ui/Card';
import { Mobile } from '../../Components/Responsive';
import InfoCard from '../../Components/InfoCard';
import background from './Background.svg';
import bdome from './BDome.svg';
import s from './Home.css';


class Home extends React.Component {
  static propTypes = {
    news: PropTypes.arrayOf(PropTypes.shape({
      title: PropTypes.string.isRequired,
      link: PropTypes.string.isRequired,
      content: PropTypes.string,
    })).isRequired,
  };

  render() {
    return (
      <Mobile>
        <div className={s.container} style={{ backgroundImage: `url(${background})` }}>
          <Card>
            <CardMedia>
              <img src={bdome} style={{ maxWidth: '80%' }} alt="SWD" />

            </CardMedia>
          </Card>
          <InfoCard title="Latest News" list={this.props.news} />
        </div>
      </Mobile>

    );
  }
}

export default Home;
