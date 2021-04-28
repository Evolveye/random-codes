<?php

class Inserter {
  const FILTER_VALUES = false;

  function insert( array $locations ) {
    $filtered_locations = $locations;
    $inserted_posts = [];

    if (self::FILTER_VALUES) {
      $existing_positions_query = new WP_Query( array( 'post_type' => 'map-location' ) );

      $existing_positions_names = array_map( function( $post ) {
        return $post->post_name;
      }, $existing_positions_query->posts );

      $filtered_locations = array_filter( $locations, function( $location ) use ($existing_positions_names) {
        return !in_array( $location->name, $existing_positions_names );
      } );
    }

    foreach ($filtered_locations as $location) {
      $location_db_data = new DbData( $location );

      $is_inserted = Utils::insert_new_location( array(
        'post_title'      => $location_db_data->post[ 'title' ],
        'post_content'    => $location_db_data->post[ 'content' ],
        'post_status'     => $location_db_data->post[ 'status' ],
        'post_type'       => $location_db_data->post[ 'type' ],
        'comment_status'  => $location_db_data->post[ 'comment_status' ],
        'ping_status'     => $location_db_data->post[ 'ping_status' ],
        'post_name'       => $location_db_data->post[ 'name' ],
        'meta_input'      => array(
          '_edit_last'                          => $location_db_data->meta[ 'edit_last' ],
          '_map_location_map'                   => $location_db_data->meta[ 'map_location_map' ],
          '_map_location_tooltip_enabled'       => $location_db_data->meta[ 'map_location_tooltip_enabled' ],
          '__map_location_tooltip_enabled'      => $location_db_data->meta[ 'map_location_tooltip_enabled_field' ],
          '_map_location_tooltip_show'          => $location_db_data->meta[ 'map_location_tooltip_show' ],
          '__map_location_tooltip_show'         => $location_db_data->meta[ 'map_location_tooltip_show_field' ],
          '_map_location_tooltip_close'         => $location_db_data->meta[ 'map_location_tooltip_close' ],
          '__map_location_tooltip_close'        => $location_db_data->meta[ 'map_location_tooltip_close_field' ],
          '_map_location_tooltip'               => $location_db_data->meta[ 'map_location_tooltip' ],
          '__map_location_tooltip'              => $location_db_data->meta[ 'map_location_tooltip_field' ],
          '_map_location_video_embed'           => $location_db_data->meta[ 'map_location_video_embed' ],
          '__map_location_video_embed'          => $location_db_data->meta[ 'map_location_video_embed_field' ],
          '_map_location_google_location-lat'   => $location_db_data->meta[ 'map_location_google_location_lat' ],
          '_map_location_google_location-lng'   => $location_db_data->meta[ 'map_location_google_location_lng' ],
          '_map_location_google_location-zoom'  => $location_db_data->meta[ 'map_location_google_location_zoom' ],
          '_map_location_google_location'       => $location_db_data->meta[ 'map_location_google_location' ],
          'location'                            => $location_db_data->meta[ 'location' ],
          '_location'                           => $location_db_data->meta[ 'location_field' ],
        ),
      ) );

      if ($is_inserted) array_push( $inserted_posts, $location_db_data->post[ 'title' ] );
    }

    return $inserted_posts;
  }
}

class DbData {
  private array $post = [
    'author'          => '1',
    'status'          => 'publish',
    'comment_status'  => 'closed',
    'ping_status'     => 'closed',
    'parent'          => '0',
    'type'            => 'map-location',
    'title'           => null,
    'name'            => null,
    'content'         => null,
  ];

  private array $meta = [
    'edit_last'                           => '1',
    'map_location_map'                    => '5',
    'map_location_tooltip_enabled'        => 'yes',
    'map_location_tooltip_enabled_field'  => 'mapify_acf_field_604cdf0453143',
    'map_location_tooltip_show'           => 'yes',
    'map_location_tooltip_show_field'     => 'mapify_acf_field_604cdf5053144',
    'map_location_tooltip_close'          => 'auto',
    'map_location_tooltip_close_field'    => 'mapify_acf_field_604cdfb374849',
    'map_location_tooltip'                => '',
    'map_location_tooltip_field'          => 'mapify_acf_field_604ce035e7d8e',
    'map_location_video_embed'            => '',
    'map_location_video_embed_field'      => 'mapify_acf_field_604ce14b0e4b9',
    'map_location_google_location_zoom'   => '7',
    'location_field'                      => 'mapify_acf_field_604ce1f6dab7d',
    'location'                            => null,
    'map_location_google_location'        => null,
    'map_location_google_location_lat'    => null,
    'map_location_google_location_lng'    => null,
  ];


  function __construct( Location $location ) {
    $lat = $location->lat;
    $lng = $location->lng;

    $this->post[ 'title' ]    = $location->brand;
    $this->post[ 'name' ]     = $location->name;
    $this->post[ 'content' ]  = $location->getDescription();

    $this->meta[ 'map_location_google_location' ]     = "$lat,$lng";
    $this->meta[ 'map_location_google_location_lat' ] = $lat;
    $this->meta[ 'map_location_google_location_lng' ] = $lng;

    $this->meta[ 'location' ] = 'a:5:{'
      . 's:12:"selected_lat";s:17:"' . $lat  . '";'
      . 's:12:"selected_lng";s:18:"' . $lng  . '";'
      . 's:12:"centered_lat";s:17:"' . $lat  . '";'
      . 's:12:"centered_lng";s:18:"' . $lng  . '";'
      . 's:10:"zoom_level";s:1:"'    . $this->meta[ 'map_location_google_location_zoom' ] . '";'
      . '}';
  }


  public function __get( $property ) {
    if (property_exists( $this, $property )) return $this->$property;
  }
}
