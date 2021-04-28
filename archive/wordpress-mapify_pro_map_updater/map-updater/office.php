<?php

class Office {
  private string $city;
  private array $locations = [];


  public function __construct( object $obj ) {
    $this->city = $obj->city;

    foreach ($obj->locations as $location) {
      if (Location::is_config_obj_valid( $location )) array_push(
        $this->locations,
        $this->create_location( $location )
      );
    }
  }


  public function __get( $property ) {
    if (property_exists( $this, $property )) return $this->$property;
  }


  public function print() {
    echo $this->city;

    foreach ($this->locations as $location) {
      echo "\n - $location->name  {  $location->lat, $location->lng  }";
    }

    echo "\n";
  }


  private function create_location( object $obj ) {
    return new Location( $this->city, $obj );
  }


  public static function is_config_obj_valid( $obj ) {
    if ($obj->city == null) return false;
    if ($obj->locations == null) return false;

    return true;
  }
}



class Location {
  private string $country;
  private string $maps_url;
  private string $phone;
  private string $street;
  private string $postal_code;
  private string $name;
  private string $id;
  private string $brand;
  private float $lat;
  private float $lng;
  private $open;


  function __construct( string $city, object $obj ) {
    $this->id           = $obj->id;
    $this->id_name      = "$obj->country-$city-$obj->name";
    $this->brand        = $obj->brand;
    $this->name         = str_replace( ' ', '-', preg_replace( '/[^-a-z ]/i', '', strtolower( $this->id_name ) ) );

    $this->country      = $obj->country;
    $this->city         = $city;
    $this->street       = $obj->street;
    $this->postal_code  = $obj->postalCode;
    $this->phone        = $obj->phone;

    $this->maps_url     = $obj->mapsUrl;
    $this->lat          = $obj->lat;
    $this->lng          = $obj->long;

    $this->open         = $obj->open;
  }


  public static function is_config_obj_valid( $obj ) {
    if ($obj->name == null) return false;
    if ($obj->lat  == null) return false;
    if ($obj->long == null) return false;

    return true;
  }


  public function __get( $property ) {
    if (property_exists( $this, $property )) return $this->$property;
  }


  public function getDescription() {
    return "$this->country :: $this->city :: $this->brand";
  }
}
